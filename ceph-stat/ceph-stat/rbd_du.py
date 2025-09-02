#!/usr/bin/env python3
"""
Ceph RBD Disk Usage API
Implements Python API equivalent to: rbd du csi-vol-85eef94a-8325-11f0-b098-ae1f4bddac18 --format=json -p fzyun-aione
Uses native librados and librbd Python APIs instead of subprocess calls.
"""

import json
import os
import sys
from typing import Dict, Any, Optional

try:
    import rados
    import rbd
except ImportError as e:
    print("Error: Ceph Python bindings not found. Please install python3-rados and python3-rbd packages.")
    print("On Ubuntu/Debian: sudo apt-get install python3-rados python3-rbd")
    print("On CentOS/RHEL: sudo yum install python3-rados python3-rbd")
    sys.exit(1)


class CephRBDDiskUsage:
    """
    A Python API wrapper for Ceph RBD disk usage commands using native librados and librbd APIs.
    Connects to Ceph using environment variables instead of configuration files.
    
    Required Environment Variables:
        CEPH_MON_HOST: Ceph monitor hosts (e.g., "10.10.22.11:6789,10.10.22.12:6789")
        CEPH_KEY: Ceph authentication key
        CEPH_CLIENT_NAME: Ceph client name (optional, default: "client.fzyun-aione")
    """
    
    def __init__(self, pool_name: str = "fzyun-aione"):
        """
        Initialize the RBD disk usage API.
        
        Args:
            pool_name (str): The Ceph pool name (default: fzyun-aione)
            
        Note: Connection configuration is read from environment variables:
            - CEPH_MON_HOST: Required. Monitor hosts
            - CEPH_KEY: Required. Authentication key  
            - CEPH_CLIENT_NAME: Optional. Client name (default: client.fzyun-aione)
        """
        self.pool_name = pool_name
        self.cluster = None
        self.ioctx = None
    
    def _connect(self):
        """Connect to Ceph cluster and open IOContext for the pool."""
        if self.cluster is None:

            # Use environment variables instead of conffile
            mon_host = os.environ.get('CEPH_MON_HOST','10.10.22.11:6789,10.10.22.12:6789,10.10.22.13:6789')
            key = os.environ.get('CEPH_KEY','AQBZcpZlJIMxBBAAR7B8KmICIt9WAeWGPYFFtQ==')
            client_name = os.environ.get('CEPH_CLIENT_NAME', 'client.fzyun-aione')
            
            if not mon_host:
                raise RuntimeError("CEPH_MON_HOST environment variable is required")
            if not key:
                raise RuntimeError("CEPH_KEY environment variable is required")
                
            print(f"Connecting with mon_host: {mon_host}")
            print(f"Using client: {client_name}")
            
            # Create rados cluster without conffile
            self.cluster = rados.Rados(name=client_name)
            
            # Set configuration from environment variables
            self.cluster.conf_set('mon_host', mon_host)
            self.cluster.conf_set('key', key)
            
            self.cluster.connect()
            self.ioctx = self.cluster.open_ioctx(self.pool_name)
    
    def _disconnect(self):
        """Disconnect from Ceph cluster."""
        if self.ioctx:
            self.ioctx.close()
            self.ioctx = None
        if self.cluster:
            self.cluster.shutdown()
            self.cluster = None
    
    def get_rbd_disk_usage(self, image_name: str, format_output: str = "json") -> Dict[str, Any]:
        """
        Get RBD disk usage information for a specific image using native librbd APIs.
        
        Args:
            image_name (str): The RBD image name (e.g., csi-vol-85eef94a-8325-11f0-b098-ae1f4bddac18)
            format_output (str): Output format (default: json)
            
        Returns:
            Dict[str, Any]: Disk usage information in JSON format
            
        Raises:
            RuntimeError: If the RBD operation fails
            rados.Error: If Ceph cluster connection fails
        """
        try:
            self._connect()
            
            # Open the RBD image
            rbd_inst = rbd.RBD()
            with rbd.Image(self.ioctx, image_name) as image:
                # Get image statistics
                stat = image.stat()
                
                # Get actual disk usage (used space)
                # This requires calculating the used blocks
                used_size = 0
                try:
                    # Use diff_iterate to calculate actual used space
                    def count_used_bytes(offset, length, exists):
                        nonlocal used_size
                        if exists:
                            used_size += length
                    
                    # Iterate through all allocated blocks
                    image.diff_iterate(0, stat['size'], None, count_used_bytes)
                except Exception:
                    # Fallback: assume full usage if diff_iterate fails
                    used_size = stat['size']
                
                # Build response similar to rbd du output
                result = {
                    "images": [{
                        "name": image_name,
                        "id": image.id(),
                        "size": stat['size'],
                        "provisioned_size": stat['size'],
                        "used_size": used_size
                    }],
                    "total_provisioned_size": stat['size'],
                    "total_used_size": used_size
                }
                
                return result
                
        except (rados.Error, rbd.Error) as e:
            raise RuntimeError(f"RBD operation failed: {str(e)}") from e
        finally:
            self._disconnect()
    
    def get_image_usage_info(self, image_name: str) -> Dict[str, Any]:
        """
        Get detailed usage information for an RBD image.
        
        Args:
            image_name (str): The RBD image name
            
        Returns:
            Dict[str, Any]: Detailed usage information including:
                - name: Image name
                - provisioned_size: Total provisioned size
                - used_size: Actually used size
                - pool: Pool name
        """
        usage_data = self.get_rbd_disk_usage(image_name)
        
        # Extract relevant information from the rbd du output
        # The exact structure depends on the Ceph version, but typically includes:
        # - images array with name, provisioned_size, used_size
        if "images" in usage_data and len(usage_data["images"]) > 0:
            image_info = usage_data["images"][0]
            return {
                "name": image_info.get("name", image_name),
                "provisioned_size": image_info.get("provisioned_size", 0),
                "used_size": image_info.get("used_size", 0),
                "pool": self.pool_name,
                "raw_data": usage_data
            }
        else:
            return {
                "name": image_name,
                "provisioned_size": 0,
                "used_size": 0,
                "pool": self.pool_name,
                "raw_data": usage_data,
                "error": "No image data found in response"
            }


def main():
    """
    Command line interface for the RBD disk usage API.
    """
    if len(sys.argv) < 2:
        print("Usage: python rbd_du.py <image_name> [pool_name]")
        print("Example: python rbd_du.py csi-vol-85eef94a-8325-11f0-b098-ae1f4bddac18 fzyun-aione")
        print("")
        print("Required Environment Variables:")
        print("  CEPH_MON_HOST - Monitor hosts (e.g., '10.10.22.11:6789,10.10.22.12:6789')")
        print("  CEPH_KEY - Authentication key")
        print("  CEPH_CLIENT_NAME - Client name (optional, default: 'client.fzyun-aione')")
        sys.exit(1)
    
    image_name = sys.argv[1]
    pool_name = sys.argv[2] if len(sys.argv) > 2 else "fzyun-aione"
    
    try:
        # Initialize the API (now uses environment variables)
        rbd_api = CephRBDDiskUsage(pool_name=pool_name)
        
        # Get usage information
        usage_info = rbd_api.get_image_usage_info(image_name)
        
        # Output JSON formatted result
        print(json.dumps(usage_info, indent=2))
        
    except Exception as e:
        error_response = {
            "error": str(e),
            "image_name": image_name,
            "pool_name": pool_name
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()