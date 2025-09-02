#!/bin/bash

source /etc/kolla/admin-openrc.sh


vcpu_options=(2 4 8 12 16 24)
ram_per_vcpu_options=(1 2 4 6)
disk_options=(40)
gpu_options=(1 2 4)

for vcpu in "${vcpu_options[@]}"; do
  for ram_per_vcpu in "${ram_per_vcpu_options[@]}"; do
    for disk in "${disk_options[@]}"; do
      for gpu in "${gpu_options[@]}"; do
        flavorid="gpu-T4-$(printf "%04d-%04d-%04d-%04d" $vcpu $(($vcpu * $ram_per_vcpu)) $disk $gpu)"
        name="gpu(T4).$(printf "%02dx%02dx%02d" $vcpu $(($vcpu * $ram_per_vcpu))) $gpu"
        ram=$(($vcpu * $ram_per_vcpu * 1024))
        openstack flavor create --id "$flavorid" --vcpus "$vcpu" --ram "$ram" --disk "$disk" --public "$name"
        openstack flavor set --property "pci_passthrough:alias=T4:$gpu" --property "quota:cpu_period=100000" --property "quota:cpu_quota=80000" "$name"
    done
  done
done
