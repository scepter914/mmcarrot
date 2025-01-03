modality = dict(use_lidar=True, use_camera=True)
data_prefix = dict(
    pts="samples/LIDAR_TOP",
    CAM_FRONT="samples/CAM_FRONT",
    CAM_FRONT_RIGHT="samples/CAM_FRONT_RIGHT",
    CAM_FRONT_LEFT="samples/CAM_FRONT_LEFT",
    CAM_BACK="samples/CAM_BACK",
    CAM_BACK_LEFT="samples/CAM_BACK_LEFT",
    CAM_BACK_RIGHT="samples/CAM_BACK_RIGHT",
    sweeps="sweeps/LIDAR_TOP",
)

camera_panels = [
    "samples/CAM_FRONT_LEFT",
    "samples/CAM_FRONT",
    "samples/CAM_FRONT_RIGHT",
    "samples/CAM_BACK_LEFT",
    "samples/CAM_BACK",
    "samples/CAM_BACK_RIGHT",
]

camera_orders = [
    "samples/CAM_FRONT",
    "samples/CAM_FRONT_RIGHT",
    "samples/CAM_FRONT_LEFT",
    "samples/CAM_BACK",
    "samples/CAM_BACK_LEFT",
    "samples/CAM_BACK_RIGHT",
]

class_colors = {
    "car": (30, 144, 255),
    "truck": (140, 0, 255),
    "construction_vehicle": (255, 255, 0),
    "bus": (111, 255, 111),
    "trailer": (0, 255, 255),
    "barrier": (0, 0, 0),
    "motorcycle": (100, 0, 30),
    "bicycle": (255, 0, 30),
    "pedestrian": (255, 200, 200),
    "traffic_cone": (120, 120, 120),
}
