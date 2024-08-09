# Rerun visualization
## Supported feature

- Dataset
  - [ ] Nuscenes
- Feature
  - [ ] LiDAR point visualization
  - [ ] Camera point visualization
  - [ ] 3D bounding box visualization
  - [ ] 3D bounging box visualization with segmentated pointcloud

## Get started

- create info file

```
# nuscenes

python tools/detection3d/create_data.py nuscenes --root-path ./data/nuscenes --out-dir ./data/nuscenes --extra-tag nuscenes
```
