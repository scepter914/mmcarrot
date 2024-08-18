import argparse
from typing import Any

import numpy as np
import rerun as rr
import rerun.blueprint as rrb
from mmdet3d.registry import MODELS
from mmengine.config import Config
from mmengine.device import get_device
from mmengine.registry import init_default_scope
from mmengine.runner import Runner, autocast, load_checkpoint
from torch import Tensor


def parse_args() -> dict[Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config",
        metavar="FILE",
        help="The config of model file or dataset loader.",
    )
    parser.add_argument(
        "visualization_config",
        metavar="FILE",
        help="The config for visualization.",
    )
    parser.add_argument(
        "--objects",
        type=str,
        default="prediction",
        choices=["prediction", "ground_truth"],
        help=
        "What objects you want to visualize. You choice from prediction, ground_truth.",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help=
        "If you choose prediction visualization, you need checkpoint file.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        choices=["train", "val", "test"],
        help="Choose dataset from train, val and test.",
    )
    parser.add_argument(
        "--bbox-score",
        type=float,
        default=0.4,
        help="Score threshold if you choose prediction visualization.",
    )
    #parser.add_argument(
    #    "--out-dir",
    #    type=str,
    #    default="work_dirs/visualization",
    #    help="",
    #)
    parser.add_argument(
        "--image-num",
        type=int,
        default=6,
        help="The number of images. 6 is default number for NuScenes dataset.",
    )
    parser.add_argument(
        "--skip-frames",
        type=int,
        default=1,
        help="The number of skip frames.",
    )
    parser.add_argument(
        "--fix-rotation",
        action="store_true",
        help="The option for fixing rotation bug. it needs for nuScenes data.",
    )
    rr.script_add_args(parser)

    args = parser.parse_args()
    return args


def update_config(
    cfg: dict[Any],
    cfg_visualization: dict[Any],
    args: argparse.Namespace,
) -> dict[Any]:

    # update batchsize
    cfg.val_dataloader.batch_size = 1
    cfg.test_dataloader.batch_size = 1

    # update multi sweep
    cfg = delete_multi_sweep(cfg)

    # update modality
    cfg.train_dataloader.dataset.dataset.modality = cfg_visualization.modality
    cfg.val_dataloader.dataset.modality = cfg_visualization.modality
    cfg.test_dataloader.dataset.modality = cfg_visualization.modality

    # update data_prefix
    cfg.train_dataloader.dataset.dataset.data_prefix = cfg_visualization.data_prefix
    cfg.val_dataloader.dataset.data_prefix = cfg_visualization.data_prefix
    cfg.test_dataloader.dataset.data_prefix = cfg_visualization.data_prefix

    # update camera_orders from args
    if args.image_num < len(cfg_visualization.camera_orders):
        cfg_visualization.camera_panels = cfg_visualization.camera_panels[
            0:args.image_num]

    return cfg, cfg_visualization


def get_class_color_list(
    class_colors: dict[Any],
    class_names: list[str],
) -> list[list[int]]:
    class_color_list = []
    for class_name in class_names:
        class_color_list.append(class_colors[class_name])
    return class_color_list


def delete_multi_sweep(cfg: dict[Any]) -> dict[Any]:
    fixed_pipeline = []
    for component in cfg.train_dataloader.dataset.dataset.pipeline:
        if component["type"] == "LoadPointsFromMultiSweeps":
            component["sweeps_num"] = 1
        fixed_pipeline.append(component)
    cfg.train_dataloader.dataset.pipeline = fixed_pipeline

    fixed_pipeline = []
    for component in cfg.val_dataloader.dataset.pipeline:
        if component["type"] == "LoadPointsFromMultiSweeps":
            component["sweeps_num"] = 1
        fixed_pipeline.append(component)
    cfg.val_dataloader.dataset.pipeline = fixed_pipeline

    fixed_pipeline = []
    for component in cfg.test_dataloader.dataset.pipeline:
        if component["type"] == "LoadPointsFromMultiSweeps":
            component["sweeps_num"] = 1
        fixed_pipeline.append(component)
    cfg.test_dataloader.dataset.pipeline = fixed_pipeline
    return cfg


def init_rerun(args: dict[Any], camera_panels: list[str]):
    # set blueprint
    sensor_space_views = [
        rrb.Spatial2DView(
            name=sensor_name,
            origin=f"world/ego_vehicle/{sensor_name}",
        ) for sensor_name in camera_panels
    ]
    blueprint = rrb.Vertical(
        rrb.Spatial3DView(
            name="3D",
            origin="world",
            # Default for `ImagePlaneDistance` so that the pinhole frustum visualizations don't take up too much space.
            # defaults=[rr.components.ImagePlaneDistance(4.0)],
            # overrides={"world/ego_vehicle": [rr.components.AxisLength(5.0)]},
        ),
        rrb.Grid(*sensor_space_views),
        row_shares=[5, 2],
    )
    rr.script_setup(args, "mmcarrot", default_blueprint=blueprint)

    # setup visualization
    rr.log("world", rr.ViewCoordinates.RIGHT_HAND_Z_UP, static=True)


def euler_to_quaternion(
    yaw: float,
    pitch: float,
    roll: float,
    fix_rotation: bool,
) -> list[float]:
    if fix_rotation:
        pitch = 0.0
        roll = 0.0
    qx = np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(
        roll / 2) * np.sin(pitch / 2) * np.sin(yaw / 2)
    qy = np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(
        roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2)
    qz = np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(
        roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2)
    qw = np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(
        roll / 2) * np.sin(pitch / 2) * np.sin(yaw / 2)
    return [qx, qy, qz, qw]


def convert_gt_objects(
    data: dict[Any],
    frame_number: int,
) -> list[Tensor]:
    if "gt_bboxes_labels" in data["data_samples"][0].eval_ann_info:
        bboxes = data["data_samples"][0].eval_ann_info["gt_bboxes_3d"]
        labels = data["data_samples"][0].eval_ann_info["gt_bboxes_labels"]
        return bboxes, labels
    else:
        print(f"frame {frame_number}: there is no objects")
        return None, None


def convert_pred_objects(
    outputs: dict[Any],
    bbox_score_threshold: float,
) -> list[Tensor]:
    bboxes = outputs[0].pred_instances_3d["bboxes_3d"].tensor.detach().cpu()
    scores = outputs[0].pred_instances_3d["scores_3d"].detach().cpu()
    labels = outputs[0].pred_instances_3d["labels_3d"].detach().cpu()
    if bbox_score_threshold is not None:
        indices = scores >= bbox_score_threshold
        bboxes = bboxes[indices]
        scores = scores[indices]
        labels = labels[indices]
    return bboxes, labels


def visualize_objects(
    bboxes: Tensor,
    labels: Tensor,
    fix_rotation: bool,
    object_colors: list[list[int]],
):
    centers = []
    sizes = []
    quaternions = []
    colors = []
    for bbox in bboxes:
        bbox = bbox.to('cpu').detach().numpy().copy()
        size = bbox[3:6]
        sizes.append(size)
        center = bbox[0:3]
        # fixed center point at z-axis
        center[2] += size[2] / 2.0
        centers.append(center)
        rotation = euler_to_quaternion(*bbox[6:9], fix_rotation)
        quaternions.append(rr.Quaternion(xyzw=rotation))

    for label in labels:
        colors.append(object_colors[label])

    rr.log(
        "world/ego_vehicle/bbox",
        rr.Boxes3D(
            centers=centers,
            sizes=sizes,
            rotations=quaternions,
            class_ids=labels,
            colors=colors,
        ),
    )


def visualize_lidar(data: dict[Any], sensor_name: list[str]):
    lidar = data["inputs"]["points"][0]
    # shape after transposing: (num_points, 3)
    points = lidar[:, :3]
    rr.log(f"world/ego_vehicle/{sensor_name}",
           rr.Points3D(points, colors=[170, 170, 170]))


def visualize_camera(
    data,
    camera_orders: list[str],
):
    for panel_name, img_path in zip(camera_orders,
                                    data["data_samples"][0].img_path):
        rr.log(f"world/ego_vehicle/{panel_name}",
               rr.ImageEncoded(path=img_path))


def main():
    args = parse_args()
    init_default_scope('mmdet3d')

    # create config
    cfg = Config.fromfile(args.config)
    cfg_visualization = Config.fromfile(args.visualization_config)

    cfg, cfg_visualization = update_config(cfg, cfg_visualization, args)
    class_color_list = get_class_color_list(cfg_visualization.class_colors,
                                            cfg.class_names)

    # build dataset
    dataset = Runner.build_dataloader(cfg.test_dataloader)

    # build model
    model = None
    if args.objects == "prediction":
        # build model and load checkpoint
        model = MODELS.build(cfg.model)
        load_checkpoint(model, args.checkpoint, map_location='cpu')
        model.to(get_device())
        model.eval()

    # init rerun visualization
    init_rerun(args, cfg_visualization.camera_panels)

    for frame_number, data in enumerate(dataset):
        if frame_number % args.skip_frames != 0:
            continue

        # set frame number
        rr.set_time_seconds("frame_number", frame_number * 0.1)

        # ego vehicle set (0, 0, 0)
        rr.log(
            "world/ego_vehicle",
            rr.Transform3D(
                translation=[0, 0, 0],
                rotation=rr.Quaternion(xyzw=[0, 0, 0, 1]),
                from_parent=False,
            ),
        )

        # bounding box
        bboxes = None
        labels = None
        if args.objects == "ground_truth":
            bboxes, labels = convert_gt_objects(data, frame_number)
        elif args.objects == "prediction":
            with autocast(enabled=True):
                outputs = model.test_step(data)
            bboxes, labels = convert_pred_objects(
                outputs,
                args.bbox_score,
            )
        if bboxes is not None:
            visualize_objects(
                bboxes,
                labels,
                args.fix_rotation,
                class_color_list,
            )

        # lidar
        visualize_lidar(data, cfg_visualization.data_prefix["pts"])

        # camera
        visualize_camera(
            data,
            cfg_visualization.camera_orders,
        )

    rr.script_teardown(args)


if __name__ == '__main__':
    main()
