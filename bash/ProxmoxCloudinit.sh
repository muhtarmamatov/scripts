#!/bin/bash
# Creats a ubuntu Cloud-Init Ready VM Template in Proxmox
#
# https://gist.github.com/chris2k20/dba14515071bd5a14e48cf8b61f7d2e2
#



export IMAGENAME="focal-server-cloudimg-amd64.img"
export IMAGEURL="https://cloud-images.ubuntu.com/focal/current/"
export STORAGE="local-zfs-cache"
export VMNAME="ubuntu-2004-cloudinit-template"
export VMID=9000
export VMMEM=2048
export VMSETTINGS="--net0 virtio,bridge=vmbr0"

wget -O ${IMAGENAME} --continue ${IMAGEURL}/${IMAGENAME} && 
qm create ${VMID} --name ${VMNAME} --memory ${VMMEM} ${VMSETTINGS} && 
qm importdisk ${VMID} ${IMAGENAME} ${STORAGE} &&
qm set ${VMID} --scsihw virtio-scsi-pci --scsi0 ${STORAGE}:vm-${VMID}-disk-0 &&
qm set ${VMID} --ide2 ${STORAGE}:cloudinit &&
qm set ${VMID} --boot c --bootdisk scsi0 &&
qm set ${VMID} --serial0 socket --vga serial0 &&
qm template ${VMID} &&
echo "TEMPLATE ${VMNAME} successfully created!" && 
echo "Now create a clone of VM with ID ${VMID} in the Webinterface.."