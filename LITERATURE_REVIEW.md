# Literature Review: Visual Navigation for Low-Flying Drones

## Problem Definitions
Visual odometry/localization without GNSS using drone footage (20-200m altitude).

## Key Algorithms & Recent Work

### 1. Feature-Based Visual Odometry
- **ORB-SLAM2/3** - Real-time SLAM using ORB features. Lightweight, open-source.
  - Papers: Mur-Artal & Tardos (2015, 2017)
  - GitHub: raulmur/ORB_SLAM2, raulmur/ORB_SLAM3
  - Suitable for: Medium-range altitude, structured scenes
  
- **AKAZE** - FAST keypoint detector with binary descriptors
  - Real-time, rotation invariant, works on drone altitude changes
  - Integrated in OpenCV

### 2. Optical Flow Methods
- **PWCNet** - Lightweight CNN-based optical flow
  - Real-time, estimates motion directly
  - Good for hover detection and localization
  
- **RAFT** - Recurrent All-Pairs Field Transform
  - More accurate but heavier than PWCNet

### 3. Place Recognition / Visual Localization
- **DenseVLAD / NetVLAD** - CNN-based image retrieval for loop closure
  - Maps reference frames to embedding space
  - Finds most similar preprocessed frame in real-time
  
- **SuperPoint** + **SuperGlue** - Deep learned keypoint matching
  - Better than SIFT/ORB for challenging conditions
  - Higher computational cost

### 4. Homography-Based Localization
- **Direct method**: Estimate planar homography between reference and current frame
- **Advantages**: Fast, works on flat terrain (fields, roads)
- **Challenge**: Non-planar scenes (buildings, trees)

### 5. Monocular Depth Estimation
- **MiDaS** - Efficient depth prediction (v2.1 is real-time capable)
  - Single image → depth map
  - Can reconstruct 3D structure for better localization

## Recommended Approach for This Task

**Hybrid Pipeline:**
1. **Preprocessing**: 
   - Extract keyframes from reference video
   - Compute AKAZE/ORB features + descriptors
   - Estimate camera intrinsics if needed
   
2. **Navigation (Real-time)**:
   - Track features or optical flow between frames
   - Match current frame to reference keyframes (NetVLAD or brute-force descriptor matching)
   - Estimate homography or perspective-n-point (PnP) for localization
   - Fuse telemetry (altitude, pitch) for scale estimation

## Open-Source Implementations
- **OpenCV** - Feature extraction, matching, homography estimation
- **ORB-SLAM3** - Full SLAM, can run on CPU
- **COLMAP** - SfM, can preprocess reference video
- **PyTorch** - NetVLAD, depth estimation models
- **YOLOX/YOLOv8** - Optional: semantic segmentation

## Expected Accuracy
- Reference baseline: ±2-5m error at 120m altitude
- Can improve with telemetry fusion and multi-frame tracking
