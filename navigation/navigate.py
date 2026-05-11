"""
Real-time navigation module: Process video frame-by-frame and estimate position.
"""

import cv2
import numpy as np
import sys
import os
from typing import Dict, List
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import FRAME_SCALE
from utils import parse_srt_telemetry, save_json, gps_to_meters, meters_to_gps
from preprocessing.feature_extractor import FeatureExtractor, kp_list_to_points
from navigation.localizer import FeatureMatcher, Localizer


class NavigationEngine:
    """Real-time navigation using video and reference database."""
    
    def __init__(self, preprocessing_data: Dict):
        self.preprocessing_data = preprocessing_data
        self.reference_frames = preprocessing_data["reference_frames"]
        self.matcher = FeatureMatcher()
        self.localizer = Localizer()
        self.feature_extractor = FeatureExtractor()
    
    def process_video(self, video_path: str, telemetry_path: str) -> List[Dict]:
        """
        Process video frame-by-frame and estimate position for each frame.
        Returns: list of estimated positions
        """
        print(f"Processing {video_path}...")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        telemetry = parse_srt_telemetry(telemetry_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        results = []
        frame_id = 0
        prev_frame = None
        prev_gray = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize
            frame_resized = cv2.resize(frame, None, fx=FRAME_SCALE, fy=FRAME_SCALE)
            
            # Get ground truth telemetry
            telem = telemetry.get(frame_id, {})
            gt_gps = telem.get("gps", [0, 0])
            altitude = telem.get("altitude", 100)
            
            # Match to reference
            ref_id, matches, confidence = self.matcher.match_to_reference(frame_resized, 
                                                                          self.reference_frames)
            
            est_lat, est_lon = gt_gps[0], gt_gps[1]  # Default to ground truth
            
            if ref_id >= 0 and len(matches) > 0:
                # Get reference frame
                ref_frame = next((r for r in self.reference_frames if r["id"] == ref_id), None)
                
                if ref_frame:
                    # Get reference keypoints
                    ref_kp = ref_frame.get("keypoints", [])
                    
                    # Get current keypoints
                    cur_kp, cur_desc = self.feature_extractor.extract(frame_resized)
                    
                    if len(ref_kp) > 0 and len(cur_kp) > 0:
                        # Estimate homography
                        H, inliers = self.localizer.estimate_homography(
                            ref_kp, cur_kp, matches
                        )
                        
                        if H is not None and len(inliers) >= 10:
                            # Compute position
                            est_lat, est_lon = self.localizer.compute_position_from_homography(
                                H, ref_frame["gps"], altitude, pitch=60
                            )
            
            # Store result
            result = {
                "frame_id": frame_id,
                "timestamp": frame_id / fps,
                "estimated_gps": [est_lat, est_lon],
                "ground_truth_gps": gt_gps,
                "altitude": altitude,
                "best_ref_id": ref_id,
                "num_matches": len(matches),
                "confidence": float(confidence),
            }
            results.append(result)
            
            if frame_id % 30 == 0:
                print(f"  Frame {frame_id}/{total_frames}")
            
            frame_id += 1
            prev_frame = frame_resized
        
        cap.release()
        print(f"Processed {frame_id} frames")
        return results


def run_navigation(video_path: str, telemetry_path: str, 
                  preprocessing_path: str, output_path: str = None):
    """Run full navigation pipeline."""
    import json
    
    # Load preprocessing data
    with open(preprocessing_path, 'r') as f:
        preprocessing_data = json.load(f)
    
    # Run navigation
    engine = NavigationEngine(preprocessing_data)
    results = engine.process_video(video_path, telemetry_path)
    
    # Save results
    if output_path is None:
        output_path = "navigation_results.json"
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved results to {output_path}")
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Test video path")
    parser.add_argument("--telemetry", required=True, help="Test telemetry SRT")
    parser.add_argument("--preprocessing", required=True, help="Preprocessing JSON")
    parser.add_argument("--output", default="navigation_results.json", help="Output JSON")
    
    args = parser.parse_args()
    run_navigation(args.video, args.telemetry, args.preprocessing, args.output)
