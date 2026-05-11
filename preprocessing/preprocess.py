"""
Preprocessing: Extract keyframes, compute features, build reference database.
"""

import cv2
import numpy as np
import os
import sys
from typing import Dict, List
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import FRAME_SCALE, KEYFRAME_INTERVAL, PREPROCESSING_DIR
from utils import parse_srt_telemetry, save_json
from feature_extractor import FeatureExtractor, kp_list_to_points


class PreprocessingPipeline:
    """Preprocess reference video to build navigation database."""
    
    def __init__(self, video_path: str, telemetry_path: str):
        self.video_path = video_path
        self.telemetry_path = telemetry_path
        self.feature_extractor = FeatureExtractor()
        
        # Load telemetry
        self.telemetry = parse_srt_telemetry(telemetry_path)
        print(f"Loaded {len(self.telemetry)} telemetry frames")
    
    def extract_keyframes(self) -> Dict[int, np.ndarray]:
        """Extract and select keyframes from video."""
        print(f"Extracting keyframes from {self.video_path}...")
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {self.video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"  Video: {total_frames} frames @ {fps} fps")
        
        keyframes = {}
        frame_id = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Select keyframes at interval
            if frame_id % KEYFRAME_INTERVAL == 0:
                # Resize for faster processing
                frame_resized = cv2.resize(frame, None, fx=FRAME_SCALE, fy=FRAME_SCALE)
                keyframes[frame_id] = frame_resized
            
            frame_id += 1
        
        cap.release()
        print(f"  Selected {len(keyframes)} keyframes")
        return keyframes
    
    def process_keyframes(self, keyframes: Dict[int, np.ndarray]) -> Dict:
        """Extract features from all keyframes."""
        print("Extracting features...")
        
        reference_frames = []
        
        for frame_id, frame in keyframes.items():
            # Extract features
            kp_list, desc = self.feature_extractor.extract(frame)
            
            if len(kp_list) == 0:
                continue
            
            # Get telemetry for this frame
            telem = self.telemetry.get(frame_id, {})
            
            ref_frame = {
                "id": frame_id,
                "keypoints": kp_list[:50],  # Store top 50 for memory efficiency
                "descriptors": desc[:50].tolist() if desc is not None else [],
                "gps": telem.get("gps", [0, 0]),
                "altitude": telem.get("altitude", 0),
                "num_features": len(kp_list),
            }
            
            reference_frames.append(ref_frame)
        
        print(f"  Extracted features for {len(reference_frames)} keyframes")
        return reference_frames
    
    def run(self, output_path: str = None) -> Dict:
        """Run full preprocessing pipeline."""
        if output_path is None:
            output_path = os.path.join(PREPROCESSING_DIR, "preprocessing_data.json")
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Extract keyframes
        keyframes = self.extract_keyframes()
        
        # Process keyframes
        reference_frames = self.process_keyframes(keyframes)
        
        # Build output
        preprocessing_data = {
            "video_path": self.video_path,
            "telemetry_path": self.telemetry_path,
            "num_reference_frames": len(reference_frames),
            "keyframe_interval": KEYFRAME_INTERVAL,
            "frame_scale": FRAME_SCALE,
            "reference_frames": reference_frames,
        }
        
        # Save
        save_json(preprocessing_data, output_path)
        print(f"Saved preprocessing data to {output_path}")
        
        return preprocessing_data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Path to reference video")
    parser.add_argument("--telemetry", required=True, help="Path to telemetry SRT file")
    parser.add_argument("--output", default=None, help="Output JSON path")
    
    args = parser.parse_args()
    
    pipeline = PreprocessingPipeline(args.video, args.telemetry)
    pipeline.run(args.output)
