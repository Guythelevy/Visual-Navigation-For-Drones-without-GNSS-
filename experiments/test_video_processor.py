"""
Test script: Process a single test video and compare with ground truth.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from navigation.navigate import run_navigation
from experiments.evaluate import evaluate_results


def test_single_video(ref_video: str, ref_telemetry: str, 
                     test_video: str, test_telemetry: str,
                     output_dir: str = "test_results"):
    """
    Run full pipeline: preprocess reference, test on new video, evaluate.
    """
    import subprocess
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Preprocess reference video
    print("=== STEP 1: PREPROCESSING REFERENCE VIDEO ===")
    preprocessing_output = os.path.join(output_dir, "preprocessing_data.json")
    
    cmd = [
        sys.executable, "src/main.py", "preprocess",
        "--video", ref_video,
        "--telemetry", ref_telemetry,
        "--output", preprocessing_output
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # Step 2: Test on new video
    print("\n=== STEP 2: RUNNING NAVIGATION ON TEST VIDEO ===")
    navigation_output = os.path.join(output_dir, "navigation_results.json")
    
    cmd = [
        sys.executable, "src/main.py", "navigate",
        "--video", test_video,
        "--telemetry", test_telemetry,
        "--preprocessing", preprocessing_output,
        "--output", navigation_output
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # Step 3: Evaluate
    print("\n=== STEP 3: EVALUATING RESULTS ===")
    eval_output = os.path.join(output_dir, "evaluation")
    
    try:
        evaluate_results(navigation_output, eval_output)
    except Exception as e:
        print(f"Evaluation error: {e}")
    
    print(f"\nTest complete. Results saved to {output_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test visual navigation on video")
    parser.add_argument("--ref-video", required=True, help="Reference training video")
    parser.add_argument("--ref-telemetry", required=True, help="Reference telemetry SRT")
    parser.add_argument("--test-video", required=True, help="Test video")
    parser.add_argument("--test-telemetry", required=True, help="Test telemetry SRT")
    parser.add_argument("--output", default="test_results", help="Output directory")
    
    args = parser.parse_args()
    
    test_single_video(args.ref_video, args.ref_telemetry, 
                     args.test_video, args.test_telemetry, 
                     args.output)
