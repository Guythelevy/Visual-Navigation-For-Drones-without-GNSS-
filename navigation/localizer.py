"""
Feature matching and localization module.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import MIN_MATCHES, RANSAC_THRESHOLD, RANSAC_MAX_ITER, MIN_INLIERS_HOMOGRAPHY
from preprocessing.feature_extractor import FeatureExtractor, kp_list_to_points


class FeatureMatcher:
    """Match features between current frame and reference database."""
    
    def __init__(self):
        self.extractor = FeatureExtractor()
    
    def match_to_reference(self, current_frame: np.ndarray, 
                          reference_frames: List[Dict]) -> Tuple[int, List[Tuple], float]:
        """
        Find best matching reference frame for current frame.
        Returns: (best_ref_id, matches_list, confidence_score)
        """
        # Extract current frame features
        current_kp, current_desc = self.extractor.extract(current_frame)
        
        if current_desc is None or len(current_desc) == 0:
            return -1, [], 0.0
        
        best_ref_id = -1
        best_matches = []
        best_confidence = 0.0
        
        # Try matching with all reference frames
        for ref_frame in reference_frames:
            ref_desc_list = ref_frame.get("descriptors", [])
            ref_id = ref_frame["id"]
            
            if not ref_desc_list or len(ref_desc_list) == 0:
                continue
            
            ref_desc = np.array(ref_desc_list, dtype=np.uint8)
            
            # Match descriptors
            matches = self.extractor.match_features(current_desc, ref_desc)
            
            if len(matches) >= MIN_MATCHES:
                # Compute confidence as inlier ratio
                confidence = len(matches) / max(len(current_desc), len(ref_desc))
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_matches = matches
                    best_ref_id = ref_id
        
        return best_ref_id, best_matches, best_confidence


class Localizer:
    """Estimate drone position using homography or PnP."""
    
    @staticmethod
    def estimate_homography(kp1: List[Tuple], kp2: List[Tuple], 
                            matches: List[Tuple]) -> Optional[Tuple[np.ndarray, List[int]]]:
        """
        Estimate homography between two frames.
        Returns: (H_matrix, inlier_indices)
        """
        if len(matches) < MIN_INLIERS_HOMOGRAPHY:
            return None, []
        
        pts1 = np.float32([kp1[m[0]][0] for m in matches])
        pts2 = np.float32([kp2[m[1]][0] for m in matches])
        
        try:
            H, inlier_mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 
                                                ransacReprojThreshold=RANSAC_THRESHOLD,
                                                maxIters=RANSAC_MAX_ITER)
            
            if H is None:
                return None, []
            
            inliers = [i for i, mask in enumerate(inlier_mask) if mask[0] > 0]
            
            if len(inliers) < MIN_INLIERS_HOMOGRAPHY:
                return None, []
            
            return H, inliers
        
        except Exception as e:
            print(f"Error in homography estimation: {e}")
            return None, []
    
    @staticmethod
    def compute_position_from_homography(H: np.ndarray, ref_gps: List[float], 
                                        altitude: float, camera_pitch: float) -> Tuple[float, float]:
        """
        Compute drone position from homography and reference GPS.
        
        Simplified approach:
        - Homography maps image coordinates
        - Use altitude and pitch to scale to ground distance
        - Add to reference GPS
        
        Returns: (latitude, longitude)
        """
        if H is None:
            return ref_gps[0], ref_gps[1]
        
        try:
            # Extract translation component from homography
            # h3 = [h31, h32, h33] relates to scale
            h31 = H[2, 0]
            h32 = H[2, 1]
            
            # Estimate ground motion (simplified)
            motion_x = H[0, 2]
            motion_y = H[1, 2]
            
            # Normalize by altitude
            scale = max(altitude / 100.0, 0.1)  # Roughly: altitude affects scale
            ground_dist_x = motion_x / scale
            ground_dist_y = motion_y / scale
            
            # Convert to GPS (approximate)
            meters_per_degree = 111000
            dlat = ground_dist_y / meters_per_degree
            dlon = ground_dist_x / (meters_per_degree * np.cos(np.radians(ref_gps[0])))
            
            new_lat = ref_gps[0] + dlat
            new_lon = ref_gps[1] + dlon
            
            return new_lat, new_lon
        
        except Exception as e:
            print(f"Error computing position: {e}")
            return ref_gps[0], ref_gps[1]
