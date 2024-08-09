import argparse
import os
from typing import List, Optional, Tuple

import mmengine
import numpy as np
import rerun as rr
import rerun.blueprint as rrb
from mmdet3d.registry import MODELS
from mmdet3d.structures import LiDARInstance3DBoxes
from mmengine.config import Config
from mmengine.device import get_device
from mmengine.registry import init_default_scope
from mmengine.runner import Runner, autocast, load_checkpoint


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", metavar="FILE")
    parser.add_argument("--checkpoint", type=str, default=None)
    parser.add_argument("--split",
                        type=str,
                        default="val",
                        choices=["train", "val"])
    parser.add_argument("--bbox-score", type=float, default=0.1)
    parser.add_argument("--out-dir",
                        type=str,
                        default="work_dirs/visualization")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    init_default_scope('mmdet3d')

    # create config
    cfg = Config.fromfile(args.config)
    cfg.val_dataloader.batch_size = 1
    cfg.test_dataloader.batch_size = 1

    # build dataset
    dataset = Runner.build_dataloader(cfg.test_dataloader)

    # build model and load checkpoint
    model = MODELS.build(cfg.model)
    load_checkpoint(model, args.checkpoint, map_location='cpu')
    model.to(get_device())
    model.eval()

    # init rerun
    sensor_space_views = [
        rrb.Spatial2DView(
            name=sensor_name,
            origin=f"world/ego_vehicle/{sensor_name}",
        ) for sensor_name in [
            'samples/LIDAR_TOP', 'samples/CAM_FRONT', 'samples/CAM_FRONT_LEFT',
            'samples/CAM_FRONT_RIGHT', 'samples/CAM_BACK',
            'samples/CAM_BACK_RIGHT', 'samples/CAM_BACK_LEFT'
        ]
    ]

    blueprint = rrb.Vertical(
        rrb.Horizontal(
            rrb.Spatial3DView(
                name="3D",
                origin="world",
                # Default for `ImagePlaneDistance` so that the pinhole frustum visualizations don't take up too much space.
                defaults=[rr.components.ImagePlaneDistance(4.0)],
                # Transform arrows for the vehicle shouldn't be too long.
                overrides={
                    "world/ego_vehicle": [rr.components.AxisLength(5.0)]
                },
            ),
            rrb.TextDocumentView(origin="description", name="Description"),
            column_shares=[3, 1],
        ),
        rrb.Grid(*sensor_space_views),
        row_shares=[4, 2],
    )
    rr.script_setup(args,
                    "rerun_example_nuscenes",
                    default_blueprint=blueprint)
    rr.log(
        "description",
        rr.TextDocument("", media_type=rr.MediaType.MARKDOWN),
        timeless=True,
    )

    for i, data in enumerate(dataset):
        lidar_path = data["data_samples"][0].lidar_path.split("/")
        file_name = "_".join(lidar_path[3:8])

        with autocast(enabled=True):
            outputs = model.test_step(data)
        bboxes = outputs[0].pred_instances_3d["bboxes_3d"].tensor.detach().cpu(
        )
        scores = outputs[0].pred_instances_3d["scores_3d"].detach().cpu()
        labels = outputs[0].pred_instances_3d["labels_3d"].detach().cpu()
        if args.bbox_score is not None:
            indices = scores >= args.bbox_score
            bboxes = bboxes[indices]
            scores = scores[indices]
            labels = labels[indices]
        bboxes = LiDARInstance3DBoxes(bboxes, box_dim=9)

        # lidar
        lidar = data["inputs"]["points"][0]
        # shape after transposing: (num_points, 3)
        points = lidar.points[:3].T
        sensor_name = 'samples/LIDAR_TOP'
        rr.log(f"world/ego_vehicle/{sensor_name}",
               rr.Points3D(points, colors=[170, 170, 170])
        # camera

        out_dir = os.path.join(args.out_dir)


if __name__ == '__main__':
    main()
