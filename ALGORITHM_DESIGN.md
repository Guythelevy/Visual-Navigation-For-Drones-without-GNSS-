# Visual Navigation Algorithm Design

## Overview
Two-stage system: **Preprocessing** (offline) → **Navigation** (real-time)

---

## PREPROCESSING STAGE

### Input
- Reference video (120fps or 30fps drone footage)
- Telemetry (GPS, altitude, pitch/roll/yaw, timestamp)
- Camera calibration (if available)

### Process

#### 1. Video Frame Extraction & Synchronization
```
For each video frame:
  - Extract frame at timestamp T
  - Match with telemetry timestamp T
  - Store: frame_id → (image, GPS, altitude, camera_angle)
```

#### 2. Keyframe Selection
```
Select keyframes to minimize redundancy:
  - For each frame, compute optical flow magnitude
  - Select frames with motion > threshold or every N frames
  - Result: Sparse set of reference frames (e.g., 5-10% of total)
```

#### 3. Feature Extraction
```
For each keyframe:
  - Detect AKAZE/ORB keypoints
  - Compute descriptors
  - Store: keyframe_db[id] = {img, keypoints, descriptors, GPS, altitude}
```

#### 4. Reference Map Construction
```
Build spatial index:
  - Group keyframes by GPS location (grid cells 10m × 10m)
  - Compute image embeddings (CNN-based or VLAD)
  - Store in searchable index
```

### Output
```
preprocessing_data.json:
{
  "camera_intrinsics": K_matrix,
  "reference_frames": [
    {
      "id": 0,
      "image_path": "...",
      "keypoints": [...],
      "descriptors": [...],
      "gps": [lat, lon],
      "altitude": 120,
      "timestamp": 1234.5,
      "embedding": [...]
    },
    ...
  ],
  "spatial_index": {...}
}
```

---

## NAVIGATION STAGE

### Input (Real-time)
- Video stream (frame-by-frame)
- Telemetry (altitude, camera pitch, timestamp)
- Reference: preprocessing_data.json

### Process

#### 1. Current Frame Processing
```
For each incoming frame:
  1. Detect AKAZE/ORB keypoints & descriptors
  2. Compute optical flow to previous frame
  3. Estimate rough motion (for hover detection)
```

#### 2. Reference Frame Matching
```
Find best matching reference frame(s):
  
  Option A (Fast): Brute-force descriptor matching
    - Match current descriptors to all reference keypoints
    - Count inliers (using RANSAC geometric test)
    - Select reference frame with max inliers
  
  Option B (Accurate): CNN-based image embedding
    - Compute current frame embedding
    - Find nearest reference frame in embedding space
    - Refine with feature matching
```

#### 3. Localization
```
Estimate drone position:
  
  a) Homography-based (for flat scenes):
     - Estimate H from feature matches
     - Use altitude & camera angle to scale
     - Position = GPS_ref + (scaled homography motion)
  
  b) PnP-based (if depth available):
     - Triangulate reference 3D points from SfM
     - Use PnP to estimate current camera pose
     - Transform to world coordinates
  
  c) Telemetry fusion:
     - Combine visual estimate with altitude change
     - If altitude changed by ΔH, scale motion
```

#### 4. Output Estimate
```
For each frame:
  estimated_position = {
    "latitude": lat,
    "longitude": lon,
    "timestamp": t,
    "confidence": conf_score
  }
```

---

## Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Keyframe spacing | 5-10 frames | Reduce redundancy |
| Feature matcher threshold | 0.7 (ORB distance) | Outlier rejection |
| RANSAC iterations | 2000 | Homography estimation |
| Embedding similarity threshold | 0.8 | Reference frame selection |
| Min inlier matches | 10 | Localization validity |

---

## Performance Expectations
- **Speed**: 30-60 FPS (with GPU acceleration)
- **Accuracy**: ±3-5m at 120m altitude
- **Latency**: <100ms per frame (real-time capable)

---

## Implementation Notes
1. Use OpenCV for classical vision operations
2. Use PyTorch/ONNX for lightweight CNN inference
3. Parallelize: frame processing → feature matching → localization
4. Cache reference descriptors in memory for speed
