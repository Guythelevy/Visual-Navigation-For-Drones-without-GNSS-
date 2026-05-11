# Visual Navigation for Drones (GNSS-Denied) "Navigation Algorithems" Ex01 under Prof. Boaz Moshe

## Overview
Real-time drone position estimation from video without GNSS, using preprocessing on reference flight data and visual features (keypoint matching, homography estimation).

By: Guy Levy 322317918
Daniel Nazrknanu 322719501


## Project Structure
```
├── LITERATURE_REVIEW.md         # Key algorithms & papers
├── ALGORITHM_DESIGN.md          # Complete pipeline design
├── README.md                     # This file
├── docs/                         # Documentation
├── src/                          # Main source code
│   ├── main.py                   # Entry point
│   ├── config.py                 # Configuration
│   └── utils.py                  # Helper functions
├── preprocessing/
│   ├── extractor.py              # Keyframe extraction
│   ├── feature_extractor.py      # AKAZE/ORB features
│   └── preprocess.py             # Main preprocessing pipeline
├── navigation/
│   ├── matcher.py                # Feature & frame matching
│   ├── localizer.py              # Position estimation (homography/PnP)
│   └── navigate.py               # Real-time navigation
├── experiments/
│   ├── evaluate.py               # Compare with ground truth
│   └── test_video_processor.py   # Test on single video
└── data/
    ├── videos/                   # Reference & test videos
    └── telemetry/                # SRT files & telemetry
```


## Algorithm Summaryy

**Preprocessing:**
1. Extract keyframes from reference video
2. Compute AKAZE features and descriptors
3. Build reference database with GPS labels

**Navigation (Real-time):**
1. Match current frame to reference frames
2. Estimate homography or camera pose
3. Compute drone position using altitude & camera angle
4. Output estimated lat/lon for each frame

## Expected Performance
- **Accuracy**: ±3-5m at 120m altitude
- **Speed**: 30+ FPS on CPU
- **Latency**: <100ms

## Key Papers
- Mur-Artal & Tardos: ORB-SLAM2/3
- Dosovitskiy et al.: FlowNet
- Arandjelović et al.: NetVLAD
