"""
Feature extraction module: AKAZE and ORB keypoint detection and description.
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict
from config import FEATURE_DETECTOR, MAX_FEATURES, AKAZE_THRESHOLD


class FeatureExtractor:
    """Extract and match features using AKAZE or ORB."""
    
    def __init__(self, detector_type: str = FEATURE_DETECTOR):
        self.detector_type = detector_type
        
        if detector_type == "AKAZE":
            self.detector = cv2.AKAZE_create(nOctaves=4, nOctaveLayers=4, threshold=AKAZE_THRESHOLD)
        elif detector_type == "ORB":
            self.detector = cv2.ORB_create(nfeatures=MAX_FEATURES, scaleFactor=1.2, nlevels=8)
        else:
            raise ValueError(f"Unknown detector: {detector_type}")
        
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    
    def extract(self, image: np.ndarray) -> Tuple[List, np.ndarray]:
        """
        Extract keypoints and descriptors from image.
        Returns: (keypoints_list, descriptors_array)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        kp, desc = self.detector.detectAndCompute(gray, None)
        
        if desc is None:
            return [], np.array([])
        
        # Convert keypoints to list of tuples for serialization
        kp_list = [(kp_i.pt, kp_i.size, kp_i.angle) for kp_i in kp]
        
        return kp_list, desc
    
    def match_features(self, desc1: np.ndarray, desc2: np.ndarray, 
                      ratio_threshold: float = 0.7) -> List[Tuple[int, int]]:
        """
        Match descriptors using Lowe's ratio test.
        Returns: list of (index_in_desc1, index_in_desc2)
        """
        if desc1 is None or desc2 is None or len(desc1) == 0 or len(desc2) == 0:
            return []
        
        matches = self.matcher.knnMatch(desc1, desc2, k=2)
        
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < ratio_threshold * n.distance:
                    good_matches.append((m.queryIdx, m.trainIdx))
        
        return good_matches


def kp_list_to_points(kp_list: List[Tuple]) -> np.ndarray:
    """Convert keypoint list format to (N, 2) points array."""
    if not kp_list:
        return np.array([])
    return np.array([kp[0] for kp in kp_list], dtype=np.float32)


def draw_matches(img1: np.ndarray, kp1: List, img2: np.ndarray, kp2: List, 
                matches: List[Tuple]) -> np.ndarray:
    """
    Draw matches between two images.
    """
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    
    out = np.zeros((max(h1, h2), w1 + w2, 3), dtype=np.uint8)
    out[:h1, :w1] = img1 if len(img1.shape) == 3 else cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    out[:h2, w1:] = img2 if len(img2.shape) == 3 else cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    
    for idx1, idx2 in matches:
        pt1 = tuple(map(int, kp1[idx1][0]))
        pt2 = tuple(map(int, kp2[idx2][0]))
        pt2_offset = (pt2[0] + w1, pt2[1])
        
        cv2.circle(out, pt1, 4, (0, 255, 0), -1)
        cv2.circle(out, pt2_offset, 4, (0, 255, 0), -1)
        cv2.line(out, pt1, pt2_offset, (0, 255, 255), 1)
    
    return out
