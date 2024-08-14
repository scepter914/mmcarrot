# Rerun visualization with mmdetection3d
## Supported feature

- Dataset
  - [x] Nuscenes
- Feature
  - [x] LiDAR point visualization
  - [x] Camera image visualization
  - [x] 3D bounding box visualization
  - [ ] 3D bounging box visualization with segmentated pointcloud

## Limitation

- Only simple visualization

From the specifications of [mmdetection3d](https://github.com/open-mmlab/mmdetection3d), only simple visualization is implemented.
View from only base_link is implemented.
This is because the data of `Runner.build_dataloader(cfg.test_dataloader)`.
It has only sensor data, and it doesn't have ego vehicle pose and timestamp.
So if you want to make something like [rerun example](https://github.com/rerun-io/rerun/tree/2acbb15ec8bf661db94139d5e3bc006f43ba1a57/examples/python/nuscenes_dataset), you need to implement visualization scripts for each dataset.

## Get started
### 1. Build and run docker

- Install

```
xhost + local:
```

- Docker build

```sh
docker build -t mmcarrot .
```

- Run

```sh
docker run -it --rm --gpus 'all,"capabilities=compute,utility,graphics"' --shm-size=64g --name mmcarrot --net host -v $PWD/:/workspace -v {path_to_dataset}:/workspace/data -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY mmcarrot
```

- For example

```sh
docker run -it --rm --gpus 'all,"capabilities=compute,utility,graphics"' --shm-size=64g --name awml -v $PWD/:/workspace -v $HOME/local/dataset:/workspace/data --net host -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY autoware-ml
```

### 2. Prepare data

- Create info file for nuscenes

```sh
python tools/create_data/create_data.py nuscenes --root-path ./data/nuscenes --out-dir ./data/nuscenes --extra-tag nuscenes
```

- Prepare own model
  - In this example, [CenterPoint](https://github.com/open-mmlab/mmdetection3d/tree/main/configs/centerpoint) is used.
  - If you want to example code, download by [pretrain model](https://download.openmmlab.com/mmdetection3d/v1.0.0_models/centerpoint/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus_20220811_031844-191a3822.pth) of [SECFPN config](https://github.com/open-mmlab/mmdetection3d/blob/main/configs/centerpoint/centerpoint_pillar02_second_secfpn_head-circlenms_8xb4-cyclic-20e_nus-3d.py) to `work_dirs/pretrain`.
  - If you want to run BEVFusion, you need to set up as [the README of BEVFusion](https://github.com/open-mmlab/mmdetection3d/tree/main/projects/BEVFusion)

### 3. Visualize

- Run on your native environment

```
rerun
```

- Run in docker

```sh
python {config_file} {visualization_config_file} \
[--fix-rotation] --checkpoint {checkpoint_file} --split test --bbox-score 0.1 --out-dir work_dirs/visualization
```

- Example with CenterPoint
  - As for parameters, please see `python tools/rerun_visualization/visualize.py -h`

```sh
python tools/rerun_visualization/visualize.py \
projects/CenterPoint/configs/centerpoint_pillar02_second_secfpn_head-circlenms_8xb4-cyclic-20e_nus-3d.py \
tools/rerun_visualization/configs/nuscenes.py \
--checkpoint work_dirs/pretrain/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus_20220811_031844-191a3822.pth \
--fix-rotation --split test --bbox-score 0.4 --objects prediction --image-num 6
```

## Tips

- If you have multiple monitors, you can expand the window of rerun desktop application and adjust for your environment
  - Below example show the visualization using monitors connected vertically

![](docs/example.png)
