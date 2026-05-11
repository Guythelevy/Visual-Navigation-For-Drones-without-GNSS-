"""
Configuration and constants for visual navigation system.
"""

import os

# Video/Frame Parameters
FPS = 30
FRAME_SCALE = 0.5  # Resize frames to 50% for faster processing
KEYFRAME_INTERVAL = 5  # Select every Nth frame as keyframe

# Feature Detection
FEATURE_DETECTOR = "AKAZE"  # Options: AKAZE, ORB
MAX_FEATURES = 500
AKAZE_THRESHOLD = 10

# Feature Matching
MATCHER_TYPE = "BruteForce"  # or "FLANN"
MATCH_RATIO_TEST = 0.7  # Lowe's ratio test threshold
MIN_MATCHES = 10

# Homography Estimation
RANSAC_THRESHOLD = 3.0  # pixels
RANSAC_MAX_ITER = 2000

# Localization
MIN_INLIERS_HOMOGRAPHY = 10
ALTITUDE_SENSITIVITY = 1.0  # Scale factor for altitude changes

# Data Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PREPROCESSING_DIR = os.path.join(BASE_DIR, "preprocessing_output")
OUTPUT_DIR = os.path.join(BASE_DIR, "results")

# Camera Intrinsics (default, can be overridden)
# For DJI Mini 3 Pro at 1080p (1920x1080)
CAMERA_INTRINSICS = {
    "focal_length": 1400,  # pixels (approximate for DJI Mini 3 Pro)
    "principal_point": (960, 540),  # image center (1920/2, 1080/2)
    "sensor_width_mm": 6.0,
    "sensor_height_mm": 4.5,
}

# Telemetry
GPS_GRID_SIZE = 10  # meters, for spatial indexing
ALTITUDE_THRESHOLD = 5.0  # meters, for detecting altitude changes

# Output
SAVE_DEBUG_FRAMES = False
VERBOSE = True
