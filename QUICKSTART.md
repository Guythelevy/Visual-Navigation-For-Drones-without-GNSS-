# QUICK START GUIDE

## 5-Minute Setup

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Prepare Data
```
data/
├── videos/
│   ├── reference.mp4   # Training video
│   └── test.mp4        # Test video
└── telemetry/
    ├── reference.srt   # Training SRT
    └── test.srt        # Test SRT
```

### 3. Run Full Pipeline
```bash
python experiments/test_video_processor.py \
  --ref-video data/videos/reference.mp4 \
  --ref-telemetry data/telemetry/reference.srt \
  --test-video data/videos/test.mp4 \
  --test-telemetry data/telemetry/test.srt
```

**Output**: `test_results/evaluation/evaluation.png` + statistics

---

## Individual Commands

### Preprocess Only
```bash
python src/main.py preprocess \
  --video data/videos/reference.mp4 \
  --telemetry data/telemetry/reference.srt
```
→ `preprocessing_data.json`

### Navigate Only
```bash
python src/main.py navigate \
  --video data/videos/test.mp4 \
  --telemetry data/telemetry/test.srt \
  --preprocessing preprocessing_data.json
```
→ `navigation_results.json`

### Evaluate Only
```bash
python experiments/evaluate.py --results navigation_results.json
```
→ `evaluation_results/evaluation.png`

---

## Key Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `LITERATURE_REVIEW.md` | Algorithm review + papers |
| `ALGORITHM_DESIGN.md` | Complete system design |
| `DOCUMENTATION.md` | Full technical documentation |
| `SETUP.md` | Installation & setup guide |
| `src/config.py` | Adjust parameters here |
| `src/main.py` | Entry point |

---

## Adjust Performance

Edit `src/config.py`:

```python
# Speed vs Accuracy
FRAME_SCALE = 0.5        # Lower = faster (0.25 for real-time)
KEYFRAME_INTERVAL = 5    # Lower = more features (higher memory)
MAX_FEATURES = 500       # Lower = faster

# Accuracy
RANSAC_MAX_ITER = 2000   # Higher = better homography
MIN_MATCHES = 10         # Higher = stricter matching
AKAZE_THRESHOLD = 10     # Lower = more features
```

---

## Test with Sample Data

To test without real videos, create dummy frames:

```python
import cv2
import numpy as np

# Create dummy reference video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('dummy_ref.mp4', fourcc, 30.0, (1920, 1080))

for i in range(300):
    frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    # Add some pattern for features
    cv2.putText(frame, f'Frame {i}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255))
    out.write(frame)

out.release()
```

Then create dummy SRT:
```
1
00:00:00,000 --> 00:00:00,033
[0.0,0.0,100.0] [0.0,60.0,0.0]
```

---

## Expected Results

**At 120m altitude:**
- Mean error: 3-5m
- 95th percentile: 8-10m
- Processing: 30 FPS

**Factors affecting accuracy:**
- ✅ Good: Urban scenes, textured ground, known altitude
- ❌ Bad: Uniform surfaces, night, seasonal changes

---

## Next Steps

1. **Collect drone footage** (DJI Mini/Air/Phantom series)
2. **Extract telemetry** (SRT files from video metadata)
3. **Split into train/test** (reference vs test videos)
4. **Run full pipeline** (preprocess → navigate → evaluate)
5. **Iterate** (adjust config.py thresholds based on results)

---

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)
