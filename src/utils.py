"""
Utility functions: telemetry parsing, coordinate transformations, etc.
"""

import os
import json
import re
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

def parse_srt_telemetry(srt_path: str) -> Dict[int, Dict]:
    """
    Parse SRT telemetry file (from DJI/Autel drones).
    Returns dict: frame_id -> {gps: [lat, lon], altitude, pitch, roll, yaw, timestamp}
    """
    telemetry_data = {}
    
    if not os.path.exists(srt_path):
        print(f"Warning: SRT file not found: {srt_path}")
        return telemetry_data
    
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        frame_id = 0
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Extract GPS: [longitude, latitude, altitude]
            gps_match = re.search(r'\[(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.?\d*)\]', line)
            if gps_match:
                lon, lat, alt = float(gps_match.group(1)), float(gps_match.group(2)), float(gps_match.group(3))
                telemetry_data[frame_id] = {
                    'gps': [lat, lon],
                    'altitude': alt,
                    'raw_line': line
                }
                frame_id += 1
        
        print(f"Parsed {frame_id} frames from {srt_path}")
        return telemetry_data
    
    except Exception as e:
        print(f"Error parsing SRT: {e}")
        return telemetry_data


def parse_generic_telemetry_csv(csv_path: str) -> Dict[int, Dict]:
    """
    Parse generic CSV telemetry (timestamp, lat, lon, altitude, pitch, roll, yaw).
    """
    telemetry_data = {}
    
    if not os.path.exists(csv_path):
        return telemetry_data
    
    try:
        import csv
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            frame_id = 0
            for row in reader:
                telemetry_data[frame_id] = {
                    'gps': [float(row.get('latitude', 0)), float(row.get('longitude', 0))],
                    'altitude': float(row.get('altitude', 0)),
                    'timestamp': row.get('timestamp', ''),
                }
                frame_id += 1
        return telemetry_data
    except Exception as e:
        print(f"Error parsing CSV telemetry: {e}")
        return telemetry_data


def gps_to_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
    """
    Convert GPS delta to approximate meters (assuming flat Earth for small distances).
    Returns: (east_meters, north_meters)
    """
    # Approximate meters per degree
    meters_per_deg_lat = 111000
    meters_per_deg_lon = 111000 * np.cos(np.radians(lat1))
    
    east = (lon2 - lon1) * meters_per_deg_lon
    north = (lat2 - lat1) * meters_per_deg_lat
    
    return east, north


def meters_to_gps(lat_ref: float, lon_ref: float, east_m: float, north_m: float) -> Tuple[float, float]:
    """
    Convert meters offset to GPS coordinates.
    Returns: (latitude, longitude)
    """
    meters_per_deg_lat = 111000
    meters_per_deg_lon = 111000 * np.cos(np.radians(lat_ref))
    
    lat_new = lat_ref + north_m / meters_per_deg_lat
    lon_new = lon_ref + east_m / meters_per_deg_lon
    
    return lat_new, lon_new


def compute_gps_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute Haversine distance in meters between two GPS points.
    """
    R = 6371000  # Earth radius in meters
    
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c


def camera_angle_to_scale(altitude: float, camera_pitch: float) -> float:
    """
    Estimate ground scale from altitude and camera pitch angle.
    Returns: pixels_per_meter (approximate)
    """
    # Simplified model: assumes camera looking down at angle
    # In practice, requires camera calibration matrix K
    angle_rad = np.radians(camera_pitch)
    
    # Rough approximation
    scale = altitude * np.tan(angle_rad) / 1000.0
    return max(scale, 0.1)


def save_json(data: Dict, output_path: str):
    """Save dictionary to JSON file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {output_path}")


def load_json(path: str) -> Dict:
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)
