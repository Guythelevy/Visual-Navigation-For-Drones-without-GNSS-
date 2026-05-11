"""
Main entry point for visual navigation system.
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.preprocess import PreprocessingPipeline
from navigation.navigate import run_navigation


def main():
    parser = argparse.ArgumentParser(description="Visual Navigation for Drones")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Preprocessing command
    preprocess_parser = subparsers.add_parser("preprocess", help="Preprocess reference video")
    preprocess_parser.add_argument("--video", required=True, help="Reference video path")
    preprocess_parser.add_argument("--telemetry", required=True, help="Telemetry SRT path")
    preprocess_parser.add_argument("--output", default=None, help="Output JSON")
    
    # Navigation command
    navigate_parser = subparsers.add_parser("navigate", help="Run real-time navigation")
    navigate_parser.add_argument("--video", required=True, help="Test video path")
    navigate_parser.add_argument("--telemetry", required=True, help="Test telemetry SRT")
    navigate_parser.add_argument("--preprocessing", required=True, help="Preprocessing JSON")
    navigate_parser.add_argument("--output", default="navigation_results.json", help="Output JSON")
    
    args = parser.parse_args()
    
    if args.command == "preprocess":
        pipeline = PreprocessingPipeline(args.video, args.telemetry)
        pipeline.run(args.output)
    
    elif args.command == "navigate":
        run_navigation(args.video, args.telemetry, args.preprocessing, args.output)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
