#!/bin/bash

apps=("curl" "wget" "qm")

for app in "${apps[@]}"; do
  if ! command -v "$app" >/dev/null 2>&1; then
    echo "================== Script required app $app does not exist, please install $app and run script ====================="
    exit 1
  fi
done

declare -A IMAGES

IMAGES=(
    ["focal-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/focal/current/"
    ["bionic-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/bionic/20230203/"
    ["focal-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/focal/20230209/"
    ["jammy-server-cloudimg-arm64.img"]="https://cloud-images.ubuntu.com/jammy/20230215/"
    ["CentOS-7-x86_64-GenericCloud-1811.qcow2"]="https://mirrors.cloud.tencent.com/centos-cloud/centos/7/images/"
    ["CentOS-7-x86_64-GenericCloud.qcow2"]="https://cloud.centos.org/centos/7/images/"
)

echo "======================== SELECT REQUIRED IMAGE TO CREATE TEMPLATE ==========================="
count=1
key=()
for os in "${!IMAGES[@]}"; do
    printf "%d. %s\n" "$count" "$os"
    (( count ++ ))
    key+=("$os")
done

read -p "Select OS (1 - $(( count - 1 ))): " choice


if [[ "$choice" -gt "$(( count -1 ))" ]]; then
    echo "------------------------ INCORRECT OS IMAGE SELECTED SELECT NUMBER BETWEEN ( 1 - $(( count -1 ))) -----------------"
    exit 1
fi

selected_os="${key[(( choice - 1 ))]}"


echo "You chose OS $selected_os continue with it yes/no: "

read -p "yes/no: " response

if [[ "$response" == "yes" ]]; then
    echo "Continuing with $selected_os"
    URL="${IMAGES[$selected_os]}${selected_os}"

    IMAGE_PATH="${HOME}/${selected_os}"

     if  curl --head --silent --fail "$URL" 2> /dev/null; then
         wget -O  ${IMAGE_PATH} --continue $URL
     else
         echo "The image does not exist in the following url ${URL} please correct url and run script again!!! "
         exit 1
     fi
     
     if [ -e "$IMAGE_PATH" ]; then

        
        IFS='.' read -ra parts <<< "$selected_os"
        template_name="${parts[0]}-${parts[1]}-template"
        template_name=${template_name//_/-}
        export IMAGENAME=$selected_os
        export STORAGE="local-lvm"
        export VMNAME=$template_name
        export VMID=9000
        export VMMEM=1024
        export VMSETTINGS="--net0 virtio,bridge=vmbr0"

        qm create ${VMID} --name "${VMNAME}" --memory ${VMMEM} ${VMSETTINGS} && 
        qm importdisk ${VMID} ${IMAGE_PATH} ${STORAGE} &&
        qm set ${VMID} --scsihw virtio-scsi-pci --scsi0 ${STORAGE}:vm-${VMID}-disk-0 &&
        qm set ${VMID} --ide2 ${STORAGE}:cloudinit &&
        qm set ${VMID} --boot c --bootdisk scsi0 &&
        qm set ${VMID} --serial0 socket --vga serial0 &&
        qm template ${VMID} &&
        echo "================= TEMPLATE ${VMNAME} successfully created! ==========================" && 
        echo "============== Now create a clone of VM with ID ${VMID} in the Webinterface.. ================="
     else
        echo "${IMAGE_PATH} does not exist"
        exit 1
     fi
else
    echo "Aborting"
fi