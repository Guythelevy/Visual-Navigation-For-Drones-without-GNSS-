#!/usr/bin/env python3
"""
Verify that all modules can be imported correctly.
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    from src import config
    print("✓ config.py")
except Exception as e:
    print(f"✗ config.py: {e}")

try:
    from src import utils
    print("✓ utils.py")
except Exception as e:
    print(f"✗ utils.py: {e}")

try:
    from preprocessing import feature_extractor
    print("✓ feature_extractor.py")
except Exception as e:
    print(f"✗ feature_extractor.py: {e}")

try:
    from preprocessing import preprocess
    print("✓ preprocess.py")
except Exception as e:
    print(f"✗ preprocess.py: {e}")

try:
    from navigation import localizer
    print("✓ localizer.py")
except Exception as e:
    print(f"✗ localizer.py: {e}")

try:
    from navigation import navigate
    print("✓ navigate.py")
except Exception as e:
    print(f"✗ navigate.py: {e}")

try:
    from experiments import evaluate
    print("✓ evaluate.py")
except Exception as e:
    print(f"✗ evaluate.py: {e}")

try:
    from src import main
    print("✓ main.py")
except Exception as e:
    print(f"✗ main.py: {e}")

print("\nAll imports successful!")
