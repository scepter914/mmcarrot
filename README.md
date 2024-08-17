
# mmcarrot

This repository gives my tools with [MMLab libraries](https://github.com/open-mmlab).

## Supported environment

- Tested by [Docker environment](Dockerfile) on Ubuntu 22.04LTS
- NVIDIA dependency: CUDA 12.1 + cuDNN 8
- Library
  - [pytorch v2.2.0](https://github.com/pytorch/pytorch/tree/v2.2.0)
  - [mmcv v2.1.0](https://github.com/open-mmlab/mmcv/tree/v2.1.0)
  - [mmdetection3d v1.4.0](https://github.com/open-mmlab/mmdetection3d/tree/v1.4.0)
  - [mmdetection v3.2.0](https://github.com/open-mmlab/mmdetection/tree/v3.2.0)
  - [mmdeploy v1.3.1](https://github.com/open-mmlab/mmdeploy/tree/v1.3.1)
  - [mmpretrain v1.2.0](https://github.com/open-mmlab/mmpretrain/tree/v1.2.0)

## Set docker environment

- Clone

```
git clone https://github.com/scepter914/mm-project-template
```

- Build docker

```sh
docker build -t mm_carrot .
```

## Tools
### [rerun_visualization](tools/rerun_visualization)

https://github.com/user-attachments/assets/16b3d085-4453-4109-b917-99ed9f40dfdc
