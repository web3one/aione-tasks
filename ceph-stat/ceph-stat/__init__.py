"""
Ceph-Stat Package
Python API for Ceph RBD disk usage operations.
"""

from .rbd_du import CephRBDDiskUsage

__version__ = "1.0.0"
__author__ = "Ceph-Stat Team"
__description__ = "Python API for Ceph RBD disk usage operations"

__all__ = ["CephRBDDiskUsage"]