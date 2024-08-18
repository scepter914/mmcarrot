# Rerun visualization with mmdetection3d

## Summary

[Rerun](https://github.com/rerun-io/rerun) visualization with [mmdetection3d](https://github.com/open-mmlab/mmdetection3d).
This tool can visualize as below

- Inference results from 3D detection models
- Ground truth with pre-process filtering like `PointsRangeFilter` of mmdetection3d function.

https://github.com/user-attachments/assets/16b3d085-4453-4109-b917-99ed9f40dfdc

## Environment
### Environment

- [rerun](https://github.com/rerun-io/rerun) 0.17.0
- The visualization code is running on Docker environment and rerun desktop application is running on native environment on Ubuntu 22.04LTS.

### Supported feature

- Dataset
  - [x] Nuscenes dataset
  - [ ] Kitti dataset
- Feature
  - [x] LiDAR point visualization
  - [x] Camera image visualization
  - [x] 3D bounding box visualization
  - [ ] 2D bounding box visualization from 3D bounding box
  - [ ] 3D bounding box visualization with segmentated pointcloud

### Note

- Only simple visualization

This tool loads dataset using [mmdetection3d](https://github.com/open-mmlab/mmdetection3d).
Because it doesn't use each dataset SDK like [rerun example](https://github.com/rerun-io/rerun/tree/main/examples/python/nuscenes_dataset), it is easily to expand for other dataset.

However, it has limitation for visualization.
From the specifications of [mmdetection3d](https://github.com/open-mmlab/mmdetection3d), only simple visualization is implemented.
First, the view from base_link is only implemented.
This is because the data of `Runner.build_dataloader(cfg.test_dataloader)` of mmdetection3d library.
It has only sensor data and it doesn't have ego vehicle pose and timestamp.
So if you want to add detail information like [rerun example](https://github.com/rerun-io/rerun/tree/2acbb15ec8bf661db94139d5e3bc006f43ba1a57/examples/python/nuscenes_dataset), you need to implement visualization scripts for each dataset.

- Different coordinate with robotics coordinate

This tool visualize by mmdetection3d coordinate. It may be different from usual robotics coordinate.

- Only python implement

[Rerun](https://github.com/rerun-io/rerun) is implemented by Rust.
Native language of library is ideal to implement because it can be mature supports.
For example, I faced some cases like "its function is only supported by C++, not for python API".
In addition, I'm also an user of Rust and strongly support [this blog](https://rerun.io/blog/why-rust), so implementing this tool by Rust is another choice for me.

However, (unfortunately for Rust users) when we use eco system of machine learning like MMLab libraries, of course it is a reasonable choice to use python.
As much as I know, [rerun](https://github.com/rerun-io/rerun) gives us mature python API and it supports many functions.
Thanks to it's supporting, this tool can choose python implementation using python API of [rerun](https://github.com/rerun-io/rerun).

## Get started
### 1. Build and run docker

- Install docker and rerun
  - https://docs.docker.com/engine/install/
  - https://rerun.io/docs/getting-started/installing-viewer
- Run command for GUI with docker

```
xhost + local:
```

- Docker build

```sh
docker build -t mmcarrot .
```

- Run docker environment

```sh
docker run -it --rm --gpus 'all,"capabilities=compute,utility,graphics"' --shm-size=64g --name mmcarrot --net host -v $PWD/:/workspace -v {path_to_dataset}:/workspace/data -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY mmcarrot
```

### 2. Prepare data

- Prepare [NuScenes dataset](https://www.nuscenes.org/)
- Create info file for NuScenes

```sh
python tools/create_data/create_data.py nuscenes --root-path ./data/nuscenes --out-dir ./data/nuscenes --extra-tag nuscenes
```

- Prepare own model
  - In this example, [CenterPoint](https://github.com/open-mmlab/mmdetection3d/tree/main/configs/centerpoint) is used.
  - If you want to example code, download by [pretrain model](https://download.openmmlab.com/mmdetection3d/v1.0.0_models/centerpoint/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus_20220811_031844-191a3822.pth) of [SECFPN config](https://github.com/open-mmlab/mmdetection3d/blob/main/configs/centerpoint/centerpoint_pillar02_second_secfpn_head-circlenms_8xb4-cyclic-20e_nus-3d.py) to `work_dirs/pretrain`.
  - If you want to run BEVFusion, you need to set up as [the README of BEVFusion](https://github.com/open-mmlab/mmdetection3d/tree/main/projects/BEVFusion)

### 3. Visualize

- Stand another terminal and Run on your native environment

```
rerun
```

- Run visualization scripts in docker environment
  - As for parameters, please see `python tools/rerun_visualization/visualize.py -h`

```sh
python tools/rerun_visualization/visualize.py \
{config_file} \
{visualization_config_file} \
--checkpoint {checkpoint_file} \
[--fix-rotation] --split [train, val, test] --bbox-score [float] --objects [ground_truth, prediction] --image-num [int]
```

- Visualize NuScenes dataset with pre-process
  - Note that this command uses about 20GB RAM

```sh
python tools/rerun_visualization/visualize.py \
projects/CenterPoint/configs/centerpoint_pillar02_second_secfpn_head-circlenms_8xb4-cyclic-20e_nus-3d.py \
tools/rerun_visualization/configs/nuscenes.py \
--fix-rotation --split test --bbox-score 0.4 --objects ground_truth --image-num 6
```

- Visualize CenterPoint inference results

```sh
python tools/rerun_visualization/visualize.py \
projects/CenterPoint/configs/centerpoint_pillar02_second_secfpn_head-circlenms_8xb4-cyclic-20e_nus-3d.py \
tools/rerun_visualization/configs/nuscenes.py \
--checkpoint work_dirs/pretrain/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus_20220811_031844-191a3822.pth \
--fix-rotation --split test --bbox-score 0.4 --objects prediction --image-num 6
```

- If you visualize on low computing device like a laptop, you should use the option of frame skipping.
  - Use about 3GB RAM as below command.

```sh
python tools/rerun_visualization/visualize.py \
projects/CenterPoint/configs/centerpoint_pillar02_second_secfpn_head-circlenms_8xb4-cyclic-20e_nus-3d.py \
tools/rerun_visualization/configs/nuscenes.py \
--checkpoint work_dirs/pretrain/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus_20220811_031844-191a3822.pth \
--fix-rotation --split test --bbox-score 0.4 --objects prediction --image-num 6 --skip-frames 10
```

## Tips

- If you have multiple monitors, you can expand the window of rerun desktop application and adjust for your environment.
  - Below example shows the visualization using monitors connected vertically.

![](docs/example.png)

## Citation

If you find this project useful in your research, please consider cite:

```
@misc{mmcarrot,
    title={Rerun visualization with mmdetection3d},
    author={Satoshi Tanaka},
    howpublished = {\url{https://github.com/scepter914/mmcarrot}},
    year={2024}
}
```
