# Configuration Guide

Edit `src/config.py` to adjust the system behavior for your specific drone and scenario.

## Common Tuning Scenarios

### Fast Real-Time Performance (30+ FPS)
```python
# In src/config.py
FRAME_SCALE = 0.25        # Aggressive downsampling
KEYFRAME_INTERVAL = 10    # Skip frames
MAX_FEATURES = 200        # Fewer features
AKAZE_THRESHOLD = 15      # Fewer keypoints
MATCHER_TYPE = "BruteForce"  # Faster than FLANN
```

### High Accuracy (at cost of speed)
```python
FRAME_SCALE = 1.0         # Full resolution
KEYFRAME_INTERVAL = 2     # More keyframes
MAX_FEATURES = 1000       # More features
AKAZE_THRESHOLD = 5       # More keypoints
RANSAC_MAX_ITER = 5000    # More robust homography
MIN_MATCHES = 20          # Stricter matching
```

### Balanced (Default)
```python
FRAME_SCALE = 0.5         # Medium resolution
KEYFRAME_INTERVAL = 5     # Balanced keyframes
MAX_FEATURES = 500        # Reasonable features
AKAZE_THRESHOLD = 10      # Default threshold
RANSAC_MAX_ITER = 2000    # Good robustness
MIN_MATCHES = 10          # Reasonable strictness
```

## Parameter Reference

### Video/Frame Processing
```python
FPS = 30                   # Input video frame rate
FRAME_SCALE = 0.5          # Resize to 50% (0.25-1.0)
KEYFRAME_INTERVAL = 5      # Take every 5th frame (1-20)
```
**Effect**: Lower FRAME_SCALE and higher KEYFRAME_INTERVAL → faster but less accurate

### Feature Detection
```python
FEATURE_DETECTOR = "AKAZE"  # "AKAZE" or "ORB"
MAX_FEATURES = 500          # Max keypoints per image (100-2000)
AKAZE_THRESHOLD = 10        # Feature strength (1-20)
```
**Effect**: Lower threshold → more features → slower but potentially better matching

### Feature Matching
```python
MATCH_RATIO_TEST = 0.7      # Lowe's ratio test (0.6-0.8)
MIN_MATCHES = 10            # Min good matches (5-50)
```
**Effect**: Higher MIN_MATCHES → stricter → fewer false positives but possible misses

### Homography Estimation
```python
RANSAC_THRESHOLD = 3.0      # Pixel error threshold (1.0-10.0)
RANSAC_MAX_ITER = 2000      # Max RANSAC iterations (500-5000)
MIN_INLIERS_HOMOGRAPHY = 10 # Min inliers for valid H (5-50)
```
**Effect**: Higher RANSAC_MAX_ITER → more robust but slower

## Troubleshooting via Config

### Problem: "Too many false matches"
```python
MATCH_RATIO_TEST = 0.6      # Make Lowe's test stricter
MIN_MATCHES = 20            # Require more good matches
RANSAC_MAX_ITER = 5000      # Better outlier rejection
```

### Problem: "No matches found"
```python
AKAZE_THRESHOLD = 5         # Detect weaker features
MAX_FEATURES = 1000         # More features to match
FRAME_SCALE = 0.75          # Better resolution
KEYFRAME_INTERVAL = 3       # More reference frames
```

### Problem: "Memory usage too high"
```python
FRAME_SCALE = 0.25          # Smaller frames
MAX_FEATURES = 200          # Fewer features
KEYFRAME_INTERVAL = 10      # Fewer keyframes
```

### Problem: "Processing too slow"
```python
FRAME_SCALE = 0.25          # Smaller frames
KEYFRAME_INTERVAL = 10      # Fewer keyframes
MAX_FEATURES = 200          # Fewer features
RANSAC_MAX_ITER = 1000      # Fewer iterations
MATCHER_TYPE = "BruteForce" # Use BF instead of FLANN
```

### Problem: "Accuracy too low (>10m error)"
```python
FRAME_SCALE = 1.0           # Full resolution
MAX_FEATURES = 1000         # More features
AKAZE_THRESHOLD = 5         # Weaker features
RANSAC_MAX_ITER = 5000      # Better homography
MIN_MATCHES = 15            # Better matching
```

## Camera Intrinsics

Update for your specific drone model:

```python
# DJI Mini 3 Pro (default)
CAMERA_INTRINSICS = {
    "focal_length": 1400,           # pixels
    "principal_point": (960, 540),  # image center for 1920x1080
}

# DJI Air 2s
CAMERA_INTRINSICS = {
    "focal_length": 1900,
    "principal_point": (960, 540),
}

# DJI Air 3
CAMERA_INTRINSICS = {
    "focal_length": 2000,
    "principal_point": (960, 540),
}

# Custom camera (compute focal length)
# If you know: sensor_width (mm), focal_length_mm, image_width (pixels)
# focal_length_pixels = (image_width / sensor_width) * focal_length_mm
```

## Advanced Options

### Using FLANN Matcher (faster for large databases)
```python
# In navigation/localizer.py, update FeatureMatcher
self.matcher = cv2.FlannBasedMatcher(
    dict(algorithm=6, table_number=12, key_size=20, multi_probe_level=2),
    dict()
)
```

### Using ORB instead of AKAZE
```python
FEATURE_DETECTOR = "ORB"
MAX_FEATURES = 500  # ORB supports more features
AKAZE_THRESHOLD = 10  # (ignored when using ORB)
```

### Custom Camera Pitch Estimation
```python
# In src/utils.py, modify camera_angle_to_scale()
def camera_angle_to_scale(altitude, camera_pitch):
    angle_rad = np.radians(camera_pitch)
    # Your custom formula here
    return scale_factor
```

## Testing Configuration Changes

```bash
# After editing src/config.py, test on single video:
python experiments/test_video_processor.py \
  --ref-video data/videos/reference.mp4 \
  --ref-telemetry data/telemetry/reference.srt \
  --test-video data/videos/test.mp4 \
  --test-telemetry data/telemetry/test.srt \
  --output results_config_v1

# Compare results
python experiments/evaluate.py --results results_config_v1/navigation_results.json
```

## Performance Benchmarks

Approximate FPS on Intel i7 (single core, 1080p video):

| FRAME_SCALE | MAX_FEATURES | FPS |
|------------|--------------|-----|
| 0.25       | 100          | 60+ |
| 0.25       | 500          | 40  |
| 0.5        | 500          | 20  |
| 0.75       | 500          | 10  |
| 1.0        | 1000         | 5   |

Memory usage (preprocessing a 10-min video):

| FRAME_SCALE | KEYFRAME_INTERVAL | Memory |
|------------|------------------|--------|
| 0.25       | 10               | 100MB  |
| 0.5        | 5                | 300MB  |
| 1.0        | 3                | 800MB  |

## Presets

Copy these entire config sections for quick presets:

```python
# PRESET: Drone Racing (ultra-fast, low accuracy)
FRAME_SCALE = 0.2
KEYFRAME_INTERVAL = 10
MAX_FEATURES = 100
AKAZE_THRESHOLD = 20

# PRESET: Precision Survey (high accuracy, slow)
FRAME_SCALE = 1.0
KEYFRAME_INTERVAL = 2
MAX_FEATURES = 1000
AKAZE_THRESHOLD = 5

# PRESET: Large Area Search (balanced)
FRAME_SCALE = 0.5
KEYFRAME_INTERVAL = 5
MAX_FEATURES = 500
AKAZE_THRESHOLD = 10
```

