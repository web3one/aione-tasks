#!/usr/bin/env python3
"""
Test script to verify the conf_file changes work correctly.
"""

import os
import sys

# Add the ceph-stat directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ceph-stat'))

from rbd_du import CephRBDDiskUsage

def test_conf_file_behavior():
    """Test that conf_file now uses current directory instead of fixed path."""
    
    print("Testing conf_file behavior...")
    print(f"Current working directory: {os.getcwd()}")
    
    # Test 1: Default behavior (should use current directory)
    print("\nTest 1: Default conf_file behavior")
    rbd_api_default = CephRBDDiskUsage()
    expected_path = os.path.join(os.getcwd(), "ceph.conf")
    print(f"Expected path: {expected_path}")
    print(f"Actual path: {rbd_api_default.conf_file}")
    
    if rbd_api_default.conf_file == expected_path:
        print("✓ Default conf_file correctly uses current directory")
    else:
        print("❌ Default conf_file does not use current directory")
        return False
    
    # Test 2: Explicit path behavior (should use provided path)
    print("\nTest 2: Explicit conf_file path")
    custom_path = "/custom/path/ceph.conf"
    rbd_api_custom = CephRBDDiskUsage(conf_file=custom_path)
    print(f"Expected path: {custom_path}")
    print(f"Actual path: {rbd_api_custom.conf_file}")
    
    if rbd_api_custom.conf_file == custom_path:
        print("✓ Custom conf_file path correctly preserved")
    else:
        print("❌ Custom conf_file path not preserved")
        return False
    
    # Test 3: Verify old behavior is gone
    print("\nTest 3: Verify old fixed path is not used")
    old_fixed_path = "/etc/ceph/ceph.conf"
    if rbd_api_default.conf_file == old_fixed_path:
        print("❌ Still using old fixed path!")
        return False
    else:
        print("✓ Old fixed path is no longer used")
    
    print("\n✅ All conf_file tests passed!")
    return True

if __name__ == "__main__":
    success = test_conf_file_behavior()
    if success:
        print("\n🎉 Configuration file changes work correctly!")
        sys.exit(0)
    else:
        print("\n❌ Configuration file changes have issues!")
        sys.exit(1)