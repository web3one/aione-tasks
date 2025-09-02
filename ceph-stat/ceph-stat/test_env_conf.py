#!/usr/bin/env python3
"""
Test script to verify environment variable support for conf_file in rbd_du.py
"""

import os
import sys
from unittest.mock import patch

# Import the CephRBDDiskUsage class
from rbd_du import CephRBDDiskUsage

def test_env_var_support():
    """Test that environment variables are used for conf_file when not specified"""
    
    # Test 1: No environment variables set, conf_file should be None
    with patch.dict(os.environ, {}, clear=True):
        rbd_api = CephRBDDiskUsage()
        assert rbd_api.conf_file is None, f"Expected None, got {rbd_api.conf_file}"
        print("✓ Test 1 passed: No env vars - conf_file is None")
    
    # Test 2: CEPH_CONF environment variable set
    test_conf_path = "/etc/ceph/ceph.conf"
    with patch.dict(os.environ, {'CEPH_CONF': test_conf_path}, clear=True):
        rbd_api = CephRBDDiskUsage()
        assert rbd_api.conf_file == test_conf_path, f"Expected {test_conf_path}, got {rbd_api.conf_file}"
        print("✓ Test 2 passed: CEPH_CONF env var used")
    
    # Test 3: CEPH_CONFIG_FILE environment variable set
    test_conf_path2 = "/opt/ceph/ceph.conf"
    with patch.dict(os.environ, {'CEPH_CONFIG_FILE': test_conf_path2}, clear=True):
        rbd_api = CephRBDDiskUsage()
        assert rbd_api.conf_file == test_conf_path2, f"Expected {test_conf_path2}, got {rbd_api.conf_file}"
        print("✓ Test 3 passed: CEPH_CONFIG_FILE env var used")
    
    # Test 4: Both environment variables set, CEPH_CONF should take priority
    with patch.dict(os.environ, {'CEPH_CONF': test_conf_path, 'CEPH_CONFIG_FILE': test_conf_path2}, clear=True):
        rbd_api = CephRBDDiskUsage()
        assert rbd_api.conf_file == test_conf_path, f"Expected {test_conf_path}, got {rbd_api.conf_file}"
        print("✓ Test 4 passed: CEPH_CONF takes priority over CEPH_CONFIG_FILE")
    
    # Test 5: Explicit conf_file parameter should override environment variables
    explicit_path = "/custom/ceph.conf"
    with patch.dict(os.environ, {'CEPH_CONF': test_conf_path}, clear=True):
        rbd_api = CephRBDDiskUsage(conf_file=explicit_path)
        assert rbd_api.conf_file == explicit_path, f"Expected {explicit_path}, got {rbd_api.conf_file}"
        print("✓ Test 5 passed: Explicit conf_file overrides env vars")
    
    print("\n🎉 All tests passed! Environment variable support is working correctly.")

if __name__ == "__main__":
    test_env_var_support()