#!/bin/bash

# remount-sdb-local-path.sh - Script to remount disk sdb to /opt/local-path-provisioner/
# This script will:
# 1. Check current mount status of sdb
# 2. Safely unmount sdb if it's currently mounted
# 3. Create the target directory /opt/local-path-provisioner/
# 4. Mount sdb to /opt/local-path-provisioner/
# 5. Update /etc/fstab for persistent mounting

set -e  # Exit on any error

echo "Starting sdb remount process to /opt/local-path-provisioner/..."

# Function to check if a mount point is active
check_mount() {
    local mount_point=$1
    if mountpoint -q "$mount_point" 2>/dev/null; then
        return 0  # mounted
    else
        return 1  # not mounted
    fi
}

# Function to safely unmount filesystem
safe_unmount() {
    local mount_point=$1
    local device=$2
    
    echo "Checking mount point: $mount_point"
    if check_mount "$mount_point"; then
        echo "Unmounting $device from $mount_point..."
        umount "$mount_point" || {
            echo "Failed to unmount $mount_point, trying force unmount..."
            umount -f "$mount_point" || {
                echo "Force unmount failed, trying lazy unmount..."
                umount -l "$mount_point"
            }
        }
        echo "Successfully unmounted $mount_point"
    else
        echo "$mount_point is not mounted, skipping..."
    fi
}

# Function to find current mount point of sdb
find_sdb_mount() {
    # Check if sdb1 is mounted
    local sdb1_mount=$(findmnt -n -o TARGET /dev/sdb1 2>/dev/null || true)
    if [ -n "$sdb1_mount" ]; then
        echo "$sdb1_mount"
        return 0
    fi
    
    # Check if sdb is mounted directly
    local sdb_mount=$(findmnt -n -o TARGET /dev/sdb 2>/dev/null || true)
    if [ -n "$sdb_mount" ]; then
        echo "$sdb_mount"
        return 0
    fi
    
    return 1
}

# Step 1: Check current sdb mount status and unmount if necessary
echo "=== Step 1: Checking current sdb mount status ==="

if [ ! -b /dev/sdb ]; then
    echo "ERROR: /dev/sdb device not found!"
    exit 1
fi

# Find current mount point of sdb
CURRENT_MOUNT=$(find_sdb_mount || true)

if [ -n "$CURRENT_MOUNT" ]; then
    echo "Found sdb mounted at: $CURRENT_MOUNT"
    
    # Determine which device is mounted (sdb or sdb1)
    if findmnt -n /dev/sdb1 >/dev/null 2>&1; then
        safe_unmount "$CURRENT_MOUNT" "/dev/sdb1"
    elif findmnt -n /dev/sdb >/dev/null 2>&1; then
        safe_unmount "$CURRENT_MOUNT" "/dev/sdb"
    fi
    
    # Remove old fstab entry if it exists
    if [ "$CURRENT_MOUNT" != "/opt/local-path-provisioner" ]; then
        echo "Removing old fstab entry for $CURRENT_MOUNT..."
        cp /etc/fstab /etc/fstab.backup.$(date +%Y%m%d_%H%M%S)
        sed -i "\|$CURRENT_MOUNT|d" /etc/fstab
    fi
else
    echo "sdb is not currently mounted"
fi

# Step 2: Prepare the disk if needed
echo "=== Step 2: Preparing disk for mounting ==="

# Check if sdb1 partition exists
if [ ! -b /dev/sdb1 ]; then
    echo "Partition /dev/sdb1 not found. Checking if sdb needs partitioning..."
    
    # Check if there's a filesystem directly on sdb
    if blkid /dev/sdb >/dev/null 2>&1; then
        echo "Found filesystem directly on /dev/sdb"
        DEVICE_TO_MOUNT="/dev/sdb"
    else
        echo "No filesystem found. Creating partition and filesystem..."
        
        # Create partition table and partition
        parted -s /dev/sdb mklabel gpt
        parted -s /dev/sdb mkpart primary ext4 0% 100%
        
        # Wait for partition to be available
        sleep 2
        
        # Create ext4 filesystem
        echo "Creating ext4 filesystem on /dev/sdb1..."
        mkfs.ext4 -F /dev/sdb1
        
        DEVICE_TO_MOUNT="/dev/sdb1"
    fi
else
    echo "Found existing partition /dev/sdb1"
    DEVICE_TO_MOUNT="/dev/sdb1"
fi

# Verify the device has a filesystem
if ! blkid "$DEVICE_TO_MOUNT" >/dev/null 2>&1; then
    echo "ERROR: No filesystem found on $DEVICE_TO_MOUNT"
    exit 1
fi

# Step 3: Create target directory
echo "=== Step 3: Creating target directory ==="
echo "Creating mount directory /opt/local-path-provisioner/..."
mkdir -p /opt/local-path-provisioner

# Step 4: Mount the device
echo "=== Step 4: Mounting $DEVICE_TO_MOUNT to /opt/local-path-provisioner/ ==="
mount "$DEVICE_TO_MOUNT" /opt/local-path-provisioner

# Verify the mount
echo "Verifying mount..."
if mountpoint -q /opt/local-path-provisioner; then
    echo "Successfully mounted $DEVICE_TO_MOUNT to /opt/local-path-provisioner/"
    df -h /opt/local-path-provisioner
else
    echo "ERROR: Failed to mount $DEVICE_TO_MOUNT to /opt/local-path-provisioner/"
    exit 1
fi

# Step 5: Update /etc/fstab for persistent mounting
echo "=== Step 5: Updating /etc/fstab ==="

# Get UUID of the device
UUID=$(blkid -s UUID -o value "$DEVICE_TO_MOUNT")
if [ -z "$UUID" ]; then
    echo "ERROR: Failed to get UUID for $DEVICE_TO_MOUNT"
    exit 1
fi

echo "Found UUID for $DEVICE_TO_MOUNT: $UUID"

# Create backup of fstab if not already done
if [ ! -f "/etc/fstab.backup.$(date +%Y%m%d_%H%M%S)" ]; then
    echo "Creating backup of /etc/fstab..."
    cp /etc/fstab /etc/fstab.backup.$(date +%Y%m%d_%H%M%S)
fi

# Check if entry already exists in fstab
if grep -q "/opt/local-path-provisioner" /etc/fstab; then
    echo "Removing existing /opt/local-path-provisioner entry from /etc/fstab..."
    sed -i '\|/opt/local-path-provisioner|d' /etc/fstab
fi

# Add new fstab entry
echo "Adding $DEVICE_TO_MOUNT entry to /etc/fstab..."
echo "UUID=$UUID /opt/local-path-provisioner ext4 defaults 0 2" >> /etc/fstab

# Verify the fstab entry
echo "Verifying /etc/fstab entry..."
if grep -q "UUID=$UUID.*\/opt\/local-path-provisioner" /etc/fstab; then
    echo "Successfully added entry to /etc/fstab:"
    grep "UUID=$UUID" /etc/fstab
else
    echo "ERROR: Failed to add entry to /etc/fstab"
    exit 1
fi

# Test fstab configuration
echo "Testing fstab configuration..."
if mount -a; then
    echo "fstab configuration test passed"
else
    echo "WARNING: fstab configuration test failed - please check manually"
fi

echo "=== Remount process completed successfully ==="
echo "Summary of actions performed:"
if [ -n "$CURRENT_MOUNT" ] && [ "$CURRENT_MOUNT" != "/opt/local-path-provisioner" ]; then
    echo "- Unmounted sdb from $CURRENT_MOUNT"
    echo "- Removed old fstab entry for $CURRENT_MOUNT"
fi
echo "- Created directory /opt/local-path-provisioner/"
echo "- Mounted $DEVICE_TO_MOUNT to /opt/local-path-provisioner/"
echo "- Added persistent mount entry to /etc/fstab"
echo ""
echo "The sdb disk is now mounted to /opt/local-path-provisioner/ and configured for persistent mounting."
echo "This location is ready for use with the local-path-provisioner in Kubernetes."