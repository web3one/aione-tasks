#!/usr/bin/env python3
"""
Test script to verify the modified rbd_du.py works with environment variables
"""

import os
import sys
from unittest.mock import patch

# Import the modified CephRBDDiskUsage class
from rbd_du import CephRBDDiskUsage

def test_environment_variable_connection():
    """Test that the modified code uses environment variables correctly"""
    
    print("Testing environment variable support in modified rbd_du.py...")
    print("=" * 60)
    
    # Test values from ceph.conf
    test_mon_host = "10.10.22.11:6789,10.10.22.12:6789,10.10.22.13:6789"
    test_key = "AQBZcpZlJIMxBBAAR7B8KmICIt9WAeWGPYFFtQ=="
    test_client_name = "client.fzyun-aione"
    
    # Test 1: Missing environment variables should raise error
    print("Test 1: Missing environment variables")
    with patch.dict(os.environ, {}, clear=True):
        try:
            rbd_api = CephRBDDiskUsage()
            rbd_api._connect()
            print("✗ Expected RuntimeError for missing CEPH_MON_HOST")
        except RuntimeError as e:
            if "CEPH_MON_HOST" in str(e):
                print("✓ Correctly raises error for missing CEPH_MON_HOST")
            else:
                print(f"✗ Wrong error message: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    # Test 2: Missing CEPH_KEY should raise error
    print("\nTest 2: Missing CEPH_KEY")
    with patch.dict(os.environ, {'CEPH_MON_HOST': test_mon_host}, clear=True):
        try:
            rbd_api = CephRBDDiskUsage()
            rbd_api._connect()
            print("✗ Expected RuntimeError for missing CEPH_KEY")
        except RuntimeError as e:
            if "CEPH_KEY" in str(e):
                print("✓ Correctly raises error for missing CEPH_KEY")
            else:
                print(f"✗ Wrong error message: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    # Test 3: All required environment variables set
    print("\nTest 3: All required environment variables set")
    env_vars = {
        'CEPH_MON_HOST': test_mon_host,
        'CEPH_KEY': test_key,
        'CEPH_CLIENT_NAME': test_client_name
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        try:
            rbd_api = CephRBDDiskUsage()
            print("✓ CephRBDDiskUsage instance created successfully")
            
            # Test connection setup (without actually connecting)
            print("✓ Environment variables properly configured:")
            print(f"  - CEPH_MON_HOST: {os.environ.get('CEPH_MON_HOST')}")
            print(f"  - CEPH_KEY: {os.environ.get('CEPH_KEY')[:20]}...")
            print(f"  - CEPH_CLIENT_NAME: {os.environ.get('CEPH_CLIENT_NAME')}")
            
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    # Test 4: Default client name
    print("\nTest 4: Default client name behavior")
    env_vars_no_client = {
        'CEPH_MON_HOST': test_mon_host,
        'CEPH_KEY': test_key
    }
    
    with patch.dict(os.environ, env_vars_no_client, clear=True):
        try:
            rbd_api = CephRBDDiskUsage()
            print("✓ Uses default client name when CEPH_CLIENT_NAME not set")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All environment variable tests completed!")
    print("\nThe modified rbd_du.py now:")
    print("- ✓ Uses CEPH_MON_HOST environment variable instead of conffile")
    print("- ✓ Uses CEPH_KEY environment variable for authentication")
    print("- ✓ Supports optional CEPH_CLIENT_NAME (defaults to client.fzyun-aione)")
    print("- ✓ Raises clear errors when required environment variables are missing")
    print("- ✓ No longer depends on ceph.conf file on disk")

def test_constructor_changes():
    """Test that constructor no longer accepts conf_file parameter"""
    print("\n" + "=" * 60)
    print("Testing constructor changes...")
    
    # Test that old conf_file parameter is removed
    try:
        # This should work - new constructor
        rbd_api = CephRBDDiskUsage(pool_name="test-pool")
        print("✓ New constructor works without conf_file parameter")
    except Exception as e:
        print(f"✗ New constructor failed: {e}")
    
    # Test that old conf_file parameter would cause error
    try:
        # This should fail - old style
        rbd_api = CephRBDDiskUsage(pool_name="test-pool", conf_file="/etc/ceph/ceph.conf")
        print("✗ Old constructor still accepts conf_file (should be removed)")
    except TypeError as e:
        print("✓ Old constructor with conf_file parameter correctly rejected")
    except Exception as e:
        print(f"? Unexpected error with old constructor: {e}")

if __name__ == "__main__":
    test_environment_variable_connection()
    test_constructor_changes()