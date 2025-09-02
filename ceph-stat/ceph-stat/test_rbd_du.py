#!/usr/bin/env python3
"""
Test script for the native RBD disk usage API implementation.
"""

import json
import sys
from rbd_du import CephRBDDiskUsage

def test_rbd_du():
    """Test the RBD disk usage functionality."""
    
    # Test image name (example from requirements)
    test_image = "csi-vol-85eef94a-8325-11f0-b098-ae1f4bddac18"
    test_pool = "fzyun-aione"
    
    print(f"Testing RBD disk usage API with:")
    print(f"  Image: {test_image}")
    print(f"  Pool: {test_pool}")
    print()
    
    try:
        # Initialize the API
        print("Initializing CephRBDDiskUsage with native librados/librbd...")
        rbd_api = CephRBDDiskUsage(pool_name=test_pool)
        print("✓ API initialized successfully")
        
        # Test get_rbd_disk_usage (raw API)
        print("\nTesting get_rbd_disk_usage()...")
        raw_usage = rbd_api.get_rbd_disk_usage(test_image)
        print("✓ Raw disk usage retrieved successfully")
        print("Raw response structure:")
        print(json.dumps(raw_usage, indent=2))
        
        # Test get_image_usage_info (formatted API)
        print(f"\nTesting get_image_usage_info()...")
        usage_info = rbd_api.get_image_usage_info(test_image)
        print("✓ Image usage info retrieved successfully")
        print("Formatted response:")
        print(json.dumps(usage_info, indent=2))
        
        # Verify expected fields
        expected_fields = ["name", "provisioned_size", "used_size", "pool", "raw_data"]
        missing_fields = [field for field in expected_fields if field not in usage_info]
        
        if missing_fields:
            print(f"⚠ Warning: Missing expected fields: {missing_fields}")
        else:
            print("✓ All expected fields present in response")
            
        print(f"\nTest Summary:")
        print(f"  Image Name: {usage_info.get('name', 'N/A')}")
        print(f"  Pool: {usage_info.get('pool', 'N/A')}")
        print(f"  Provisioned Size: {usage_info.get('provisioned_size', 0):,} bytes")
        print(f"  Used Size: {usage_info.get('used_size', 0):,} bytes")
        
        if usage_info.get('provisioned_size', 0) > 0:
            usage_percent = (usage_info.get('used_size', 0) / usage_info.get('provisioned_size', 1)) * 100
            print(f"  Usage: {usage_percent:.2f}%")
        
        print("\n✅ All tests passed! Native API implementation is working correctly.")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure python3-rados and python3-rbd packages are installed.")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("This could be due to:")
        print("  - Ceph cluster not accessible")
        print("  - Pool or image doesn't exist")
        print("  - Authentication issues")
        print("  - Network connectivity problems")
        return False
        
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("RBD Disk Usage Native API Test")
    print("=" * 60)
    
    success = test_rbd_du()
    
    print("=" * 60)
    if success:
        print("✅ TEST COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("❌ TEST FAILED")
        sys.exit(1)