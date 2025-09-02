#!/bin/bash

# clear-lvm.sh - Script to clean up LVM configuration and format sdb disk
# This script will:
# 1. Unmount specified filesystems
# 2. Remove logical volumes
# 3. Remove volume group
# 4. Remove physical volume
# 5. Format sdb disk
# 6. Mount sdb to /mnt/disks/

set -e  # Exit on any error

echo "Starting LVM cleanup process..."

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

# Step 1: Unmount the filesystems
echo "=== Step 1: Unmounting filesystems ==="
safe_unmount "/data" "/dev/mapper/test--vg-test_2"
safe_unmount "/var/lib/etcd" "/dev/mapper/test--vg-test_1"

# Step 2: Remove logical volumes
echo "=== Step 2: Removing logical volumes ==="

# Get all logical volumes in test-vg volume group
LVS=$(lvs --noheadings -o lv_name test-vg 2>/dev/null | tr -d ' ' || true)

if [ -n "$LVS" ]; then
    for lv in $LVS; do
        echo "Removing logical volume: $lv"
        lvremove -f "/dev/test-vg/$lv"
    done
    echo "All logical volumes removed successfully"
else
    echo "No logical volumes found in test-vg"
fi

# Step 3: Remove volume group
echo "=== Step 3: Removing volume group ==="
if vgs test-vg >/dev/null 2>&1; then
    echo "Removing volume group: test-vg"
    vgremove -f test-vg
    echo "Volume group removed successfully"
else
    echo "Volume group test-vg not found, skipping..."
fi

# Step 4: Remove physical volume
echo "=== Step 4: Removing physical volume ==="
if pvs /dev/sdb >/dev/null 2>&1; then
    echo "Removing physical volume: /dev/sdb"
    pvremove -f /dev/sdb
    echo "Physical volume removed successfully"
else
    echo "Physical volume /dev/sdb not found, skipping..."
fi

# Step 5: Format sdb disk
echo "=== Step 5: Formatting /dev/sdb disk ==="
if [ -b /dev/sdb ]; then
    echo "Wiping filesystem signatures from /dev/sdb..."
    wipefs -a /dev/sdb
    
    echo "Creating new partition table on /dev/sdb..."
    parted -s /dev/sdb mklabel gpt
    
    echo "Disk /dev/sdb has been cleaned and formatted"
    
    # Show final disk status
    echo "Final disk status:"
    lsblk /dev/sdb
else
    echo "ERROR: /dev/sdb device not found!"
    exit 1
fi

# Step 6: Mount sdb to /mnt/disks/
echo "=== Step 6: Creating filesystem and mounting /dev/sdb ==="

# Create a single partition on the disk
echo "Creating partition on /dev/sdb..."
parted -s /dev/sdb mkpart primary ext4 0% 100%

# Wait for the partition to be available
sleep 2

# Format the partition with ext4
echo "Creating ext4 filesystem on /dev/sdb1..."
mkfs.ext4 -F /dev/sdb1

# Create mount directory if it doesn't exist
echo "Creating mount directory /mnt/disks/..."
mkdir -p /mnt/disks

# Mount the partition
echo "Mounting /dev/sdb1 to /mnt/disks/..."
mount /dev/sdb1 /mnt/disks

# Verify the mount
echo "Verifying mount..."
if mountpoint -q /mnt/disks; then
    echo "Successfully mounted /dev/sdb1 to /mnt/disks/"
    df -h /mnt/disks
else
    echo "ERROR: Failed to mount /dev/sdb1 to /mnt/disks/"
    exit 1
fi

# Step 7: Add entry to /etc/fstab for persistent mounting
echo "=== Step 7: Adding entry to /etc/fstab ==="

# Get UUID of the partition
UUID=$(blkid -s UUID -o value /dev/sdb1)
if [ -z "$UUID" ]; then
    echo "ERROR: Failed to get UUID for /dev/sdb1"
    exit 1
fi

echo "Found UUID for /dev/sdb1: $UUID"

# Create backup of fstab
echo "Creating backup of /etc/fstab..."
cp /etc/fstab /etc/fstab.backup.$(date +%Y%m%d_%H%M%S)

# Check if entry already exists in fstab
if grep -q "/mnt/disks" /etc/fstab; then
    echo "Removing existing /mnt/disks entry from /etc/fstab..."
    sed -i '\|/mnt/disks|d' /etc/fstab
fi

# Add new fstab entry
echo "Adding /dev/sdb1 entry to /etc/fstab..."
echo "UUID=$UUID /mnt/disks ext4 defaults 0 2" >> /etc/fstab

# Verify the fstab entry
echo "Verifying /etc/fstab entry..."
if grep -q "UUID=$UUID.*\/mnt\/disks" /etc/fstab; then
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

echo "=== LVM cleanup and disk setup completed successfully ==="
echo "Summary of actions performed:"
echo "- Unmounted /data and /var/lib/etcd"
echo "- Removed all logical volumes from test-vg"
echo "- Removed volume group test-vg"
echo "- Removed physical volume from /dev/sdb"
echo "- Formatted /dev/sdb with clean GPT partition table"
echo "- Created partition and ext4 filesystem on /dev/sdb1"
echo "- Mounted /dev/sdb1 to /mnt/disks/"
echo "- Added persistent mount entry to /etc/fstab"
echo ""
echo "The /dev/sdb disk is now clean, formatted, mounted to /mnt/disks/, and configured for persistent mounting."