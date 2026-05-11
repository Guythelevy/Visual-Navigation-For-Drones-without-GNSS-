# Setup Instructions

## Requirements
- Python 3.8+
- pip or conda

## Installation

### 1. Clone the repository
```bash
git clone <repo_url>
cd NivutEx1-2
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Quick Start

### Preprocess Reference Video
```bash
python src/main.py preprocess \
  --video data/videos/reference.mp4 \
  --telemetry data/telemetry/reference.srt \
  --output preprocessing_data.json
```

### Run Navigation on Test Video
```bash
python src/main.py navigate \
  --video data/videos/test.mp4 \
  --telemetry data/telemetry/test.srt \
  --preprocessing preprocessing_data.json \
  --output results.json
```

### Evaluate Results
```bash
python experiments/evaluate.py \
  --results results.json \
  --output evaluation_results
```

### Full Test (All Steps)
```bash
python experiments/test_video_processor.py \
  --ref-video data/videos/reference.mp4 \
  --ref-telemetry data/telemetry/reference.srt \
  --test-video data/videos/test.mp4 \
  --test-telemetry data/telemetry/test.srt \
  --output test_results
```

## Input Data Format

### Videos
- Format: MP4, AVI (OpenCV compatible)
- Resolution: 1080p recommended
- FPS: 30 or 60

### Telemetry (SRT Format)
DJI/Autel SRT format with GPS, altitude, pitch/roll/yaw:
```
1
00:00:00,000 --> 00:00:00,033
[GPS_Longitude,GPS_Latitude,Altitude] [Yaw,Pitch,Roll]
```

## Output Format

### Results JSON
```json
[
  {
    "frame_id": 0,
    "timestamp": 0.0,
    "estimated_gps": [latitude, longitude],
    "ground_truth_gps": [latitude, longitude],
    "altitude": 120,
    "best_ref_id": 0,
    "num_matches": 25,
    "confidence": 0.85
  },
  ...
]
```

## Customization

Edit `src/config.py` to adjust:
- Feature detector (AKAZE, ORB)
- Keyframe interval
- Frame scaling factor
- RANSAC parameters
- Camera intrinsics

## Troubleshooting

### No matches found
- Reduce frame scale in config.py
- Increase MAX_FEATURES
- Check video quality and overlap between reference and test

### Out of memory
- Reduce FRAME_SCALE
- Reduce keyframe count (increase KEYFRAME_INTERVAL)

## References
- ORB-SLAM: https://github.com/raulmur/ORB_SLAM2
- NetVLAD: https://github.com/Relja/netvlad
- OpenCV: https://docs.opencv.org
