"""
Evaluation script: Compare estimated positions with ground truth telemetry.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import compute_gps_distance


def evaluate_results(results_path: str, output_dir: str = "evaluation_results"):
    """
    Evaluate navigation results against ground truth.
    Computes error statistics and generates plots.
    """
    # Load results
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    print(f"Evaluating {len(results)} frames...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Compute errors
    errors_m = []  # errors in meters
    est_lats = []
    est_lons = []
    gt_lats = []
    gt_lons = []
    frame_ids = []
    
    for result in results:
        est_gps = result["estimated_gps"]
        gt_gps = result["ground_truth_gps"]
        frame_id = result["frame_id"]
        
        # Compute distance error
        error = compute_gps_distance(gt_gps[0], gt_gps[1], est_gps[0], est_gps[1])
        
        errors_m.append(error)
        est_lats.append(est_gps[0])
        est_lons.append(est_gps[1])
        gt_lats.append(gt_gps[0])
        gt_lons.append(gt_gps[1])
        frame_ids.append(frame_id)
    
    errors_m = np.array(errors_m)
    
    # Statistics
    mean_error = np.mean(errors_m)
    median_error = np.median(errors_m)
    max_error = np.max(errors_m)
    std_error = np.std(errors_m)
    
    print("\n=== EVALUATION RESULTS ===")
    print(f"Mean error:     {mean_error:.2f} m")
    print(f"Median error:   {median_error:.2f} m")
    print(f"Std error:      {std_error:.2f} m")
    print(f"Max error:      {max_error:.2f} m")
    
    # Generate plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Error over time
    axes[0, 0].plot(frame_ids, errors_m, 'b-', linewidth=1)
    axes[0, 0].axhline(mean_error, color='r', linestyle='--', label=f'Mean: {mean_error:.1f}m')
    axes[0, 0].set_xlabel("Frame ID")
    axes[0, 0].set_ylabel("Error (m)")
    axes[0, 0].set_title("Localization Error vs Frame")
    axes[0, 0].legend()
    axes[0, 0].grid()
    
    # Error histogram
    axes[0, 1].hist(errors_m, bins=30, edgecolor='black')
    axes[0, 1].set_xlabel("Error (m)")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].set_title("Error Distribution")
    axes[0, 1].grid()
    
    # Trajectory comparison
    axes[1, 0].scatter(gt_lons, gt_lats, label="Ground Truth", s=2, alpha=0.5)
    axes[1, 0].scatter(est_lons, est_lats, label="Estimated", s=2, alpha=0.5)
    axes[1, 0].set_xlabel("Longitude")
    axes[1, 0].set_ylabel("Latitude")
    axes[1, 0].set_title("Estimated vs Ground Truth Trajectory")
    axes[1, 0].legend()
    axes[1, 0].grid()
    
    # CDF of errors
    sorted_errors = np.sort(errors_m)
    cdf = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors)
    axes[1, 1].plot(sorted_errors, cdf, 'b-', linewidth=2)
    axes[1, 1].set_xlabel("Error (m)")
    axes[1, 1].set_ylabel("Cumulative Probability")
    axes[1, 1].set_title("Error CDF")
    axes[1, 1].grid()
    
    plt.tight_layout()
    plot_path = os.path.join(output_dir, "evaluation.png")
    plt.savefig(plot_path, dpi=150)
    print(f"\nSaved plot to {plot_path}")
    
    # Save statistics
    stats = {
        "mean_error_m": float(mean_error),
        "median_error_m": float(median_error),
        "std_error_m": float(std_error),
        "max_error_m": float(max_error),
        "num_frames": len(results),
    }
    
    stats_path = os.path.join(output_dir, "statistics.json")
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Saved statistics to {stats_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Navigation results JSON")
    parser.add_argument("--output", default="evaluation_results", help="Output directory")
    
    args = parser.parse_args()
    evaluate_results(args.results, args.output)
