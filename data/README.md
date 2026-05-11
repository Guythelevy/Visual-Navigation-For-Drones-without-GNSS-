# Data Directory

Place your drone footage and telemetry files here.

## Directory Structure

```
data/
├── videos/
│   ├── reference.mp4      # Training video (any DJI/Autel/HiFly drone)
│   └── test.mp4           # Test video (for evaluation)
└── telemetry/
    ├── reference.srt      # Training telemetry (DJI SRT format)
    └── test.srt           # Test telemetry (same format)
```

## Supported Formats

### Videos
- **Format**: MP4, AVI, MOV, MKV (OpenCV compatible)
- **Resolution**: 1080p recommended (720p min, 4K ok but slower)
- **Frame rate**: 30 fps (24, 60, 120 fps also supported)
- **Duration**: 1-30 minutes (longer = more features, slower preprocessing)

### Telemetry (SRT Files)

SRT format from DJI drones (can be extracted using DJI software or VLC):

```
1
00:00:00,000 --> 00:00:00,033
[GPS_Longitude,GPS_Latitude,Altitude] [Yaw,Pitch,Roll]

2
00:00:00,033 --> 00:00:00,066
[GPS_Longitude,GPS_Latitude,Altitude] [Yaw,Pitch,Roll]

...
```

**Example:**
```
1
00:00:00,000 --> 00:00:00,033
[24.7965,50.4501,119.2] [0.0,60.0,0.0]
```

### Where to Get Drone Footage

**DJI Drones:**
- DJI Mini 3 Pro, Air 2s, Air 3, Phantom 4
- Telemetry in MP4 metadata
- Extract SRT: DJI Assistant 2, VLC (Subtitles menu)

**Autel Robotics:**
- Autel Robotics Nano Plus, EVO II
- SRT export in official app

**Other Drones:**
- Most modern drones record GPS to metadata
- Convert to SRT format (see format above)

## Sample Data Format

Create dummy test data:

```python
import cv2
import numpy as np

# Create dummy video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('data/videos/test.mp4', fourcc, 30.0, (1920, 1080))

for i in range(300):  # 10 seconds @ 30 fps
    frame = np.random.randint(100, 150, (1080, 1920, 3), dtype=np.uint8)
    # Add some pattern
    cv2.rectangle(frame, (100 + i, 100), (200 + i, 200), (255, 0, 0), -1)
    out.write(frame)

out.release()
```

Create dummy SRT:

```
1
00:00:00,000 --> 00:00:00,033
[24.7965,50.4501,100.0] [0.0,60.0,0.0]

2
00:00:00,033 --> 00:00:00,066
[24.7966,50.4502,100.0] [0.0,60.0,0.0]

3
00:00:00,066 --> 00:00:00,099
[24.7967,50.4503,100.0] [0.0,60.0,0.0]
```

## Expected File Sizes

- Video (10 min, 1080p): ~200-500 MB
- SRT (10 min): ~500 KB
- Total per flight: ~500 MB

## Notes

- **Reference vs Test**: Use one video for preprocessing (reference), different one for testing
- **Overlap**: Test video should be from same location (but different time/angle recommended)
- **Quality**: Higher texture = better features (cities > fields > deserts)
- **Altitude**: Consistent altitude recommended (60-200m optimal)
- **Camera Angle**: Typically 60° pitch (downward looking)

## Troubleshooting

**Error: "Cannot open video"**
- Check file path exists
- Try converting to MP4 (FFmpeg)
- Verify video codec supported by OpenCV

**Error: "Empty SRT"**
- Verify SRT format matches DJI specification
- Check that GPS/altitude are valid numbers
- Try opening in VLC to validate

**No matches found**
- Use longer video (more frames = more features)
- Use video with textured scenes
- Check reference and test video have overlap

