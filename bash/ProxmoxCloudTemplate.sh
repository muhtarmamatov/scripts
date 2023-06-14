#!/bin/bash

export IMAGENAME="CentOS-7-x86_64-GenericCloud.qcow2"
export STORAGE="local-lvm"
export VMNAME="centos7-1809-cloud-template"
export VMID=9000
export VMMEM=2048
export VMSETTINGS="--net0 virtio,bridge=vmbr0"

# wget -O ${IMAGENAME} --continue ${IMAGEURL}/${IMAGENAME} && 
qm create ${VMID} --name ${VMNAME} --memory ${VMMEM} ${VMSETTINGS} &&
cd /var/lib/vz/template/iso/ &&
qm importdisk ${VMID} ${IMAGENAME} ${STORAGE} &&
qm set ${VMID} --scsihw virtio-scsi-pci --scsi0 ${STORAGE}:vm-${VMID}-disk-0 &&
qm set ${VMID} --ide2 ${STORAGE}:cloudinit &&
qm set ${VMID} --boot c --bootdisk scsi0 &&
qm set ${VMID} --serial0 socket --vga serial0 &&
qm template ${VMID} &&
echo "TEMPLATE ${VMNAME} successfully created!" && 
echo "Now create a clone of VM with ID ${VMID} in the Webinterface.."