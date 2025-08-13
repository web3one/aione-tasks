#!/usr/bin/env python3
"""
Test script to verify Python version in the Docker container.
This script should be run inside the Docker container to verify Python 3.12.9 installation.
"""

import sys
import platform

def main():
    print("Python Version Information:")
    print(f"Python version: {sys.version}")
    print(f"Python version info: {sys.version_info}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Check if Python version is 3.12.x
    if sys.version_info.major == 3 and sys.version_info.minor == 12:
        print("✓ SUCCESS: Python 3.12 is installed")
        if sys.version_info.micro == 9:
            print("✓ SUCCESS: Python 3.12.9 is installed")
        else:
            print(f"⚠ WARNING: Python 3.12.{sys.version_info.micro} is installed, not 3.12.9")
    else:
        print(f"✗ ERROR: Expected Python 3.12.x, but got {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())