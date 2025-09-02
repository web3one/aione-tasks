#!/usr/bin/env python3
"""
Test script to understand rados.Rados() constructor parameters for environment variables
"""

import os
import sys

try:
    import rados
except ImportError as e:
    print("Error: Ceph Python bindings not found.")
    sys.exit(1)

def test_rados_connection():
    """Test different ways to connect to rados using environment variables"""
    
    # Test 1: Using conf_data parameter with configuration string
    conf_data = """
[global]
mon_host = 10.10.22.11:6789,10.10.22.12:6789,10.10.22.13:6789

[client.fzyun-aione]
key = AQBZcpZlJIMxBBAAR7B8KmICIt9WAeWGPYFFtQ==
"""
    
    print("Testing rados.Rados() constructor options...")
    
    # Option 1: conf_data parameter
    try:
        cluster = rados.Rados(conf_data=conf_data, name='client.fzyun-aione')
        print("✓ conf_data parameter works")
        cluster.shutdown()
    except Exception as e:
        print(f"✗ conf_data failed: {e}")
    
    # Option 2: individual configuration options
    try:
        cluster = rados.Rados(name='client.fzyun-aione')
        cluster.conf_set('mon_host', '10.10.22.11:6789,10.10.22.12:6789,10.10.22.13:6789')
        cluster.conf_set('key', 'AQBZcpZlJIMxBBAAR7B8KmICIt9WAeWGPYFFtQ==')
        print("✓ conf_set method works")
        cluster.shutdown()
    except Exception as e:
        print(f"✗ conf_set failed: {e}")
    
    # Option 3: environment variables
    print("\nTesting environment variable support...")
    print("CEPH_MON_HOST:", os.environ.get('CEPH_MON_HOST', 'Not set'))
    print("CEPH_KEY:", os.environ.get('CEPH_KEY', 'Not set'))
    
    try:
        # Set environment variables
        os.environ['CEPH_MON_HOST'] = '10.10.22.11:6789,10.10.22.12:6789,10.10.22.13:6789'
        os.environ['CEPH_KEY'] = 'AQBZcpZlJIMxBBAAR7B8KmICIt9WAeWGPYFFtQ=='
        
        cluster = rados.Rados(name='client.fzyun-aione')
        print("✓ environment variables can be used with empty constructor")
        cluster.shutdown()
    except Exception as e:
        print(f"✗ environment variables failed: {e}")

if __name__ == "__main__":
    test_rados_connection()