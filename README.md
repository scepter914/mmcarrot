# mmcarrot

This repository is my tools with [mm series](https://github.com/open-mmlab).

## Supported environment

- Tested by [Docker environment](Dockerfile) on Ubuntu 22.04LTS
- NVIDIA dependency: CUDA 12.1 + cuDNN 8
- Library
  - [pytorch v2.2.0](https://github.com/pytorch/pytorch/tree/v2.2.0)
  - [mmcv v2.1.0](https://github.com/open-mmlab/mmcv/tree/v2.1.0)
  - [mmdetection3d v1.4.0](https://github.com/open-mmlab/mmdetection3d/tree/v1.4.0)
  - [mmdetection v3.2.0](https://github.com/open-mmlab/mmdetection/tree/v3.3.0)
  - [mmdeploy v1.3.1](https://github.com/open-mmlab/mmdeploy/tree/v1.3.1)

## Set environment

- Clone

```
git clone https://github.com/scepter914/mm-project-template
```

- Build docker

```sh
docker build -t mm_carrot .
```

## Tools
### Rerun visualization

- [rerun_visualization](tools/rerun_visualization)
