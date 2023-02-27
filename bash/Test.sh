#!/bin/bash

# if ! [ -x $(command -v curl) ] || ! [ -x $(command -v wget) ]; then
#     echo 'Error: curl or wget does not exist on te system, please install.' >&2
#     exit 1
# fi

# read -p "Enter image name ex: focal-server-cloudimg-amd64.img:  " IMAGENAME
# read -p "Enter Download link without image ex: https://cloud-images.ubuntu.com/focal/current/:  " IMAGEURL

# if  curl --head --silent --fail "$IMAGEURL$IMAGENAME" 2> /dev/null; then
#         wget -O ${IMAGENAME} --continue ${IMAGEURL}${IMAGENAME}
#     else
#         echo "The image does not exist in following url ${IMAGEURL}${IMAGENAME} please correct url and run script again!!! "
# fi

IMAGES=( "focal-server-cloudimg-amd64.img":"https://cloud-images.ubuntu.com/focal/current/"
         "bionic-server-cloudimg-amd64.img":"https://cloud-images.ubuntu.com/bionic/20230203/"
         "focal-server-cloudimg-amd64.img":"https://cloud-images.ubuntu.com/focal/20230209/"
         "jammy-server-cloudimg-arm64.img":"https://cloud-images.ubuntu.com/jammy/20230215/"
         "CentOS-7-x86_64-GenericCloud-1811.qcow2":"https://mirrors.cloud.tencent.com/centos-cloud/centos/7/images/"
         "CentOS-7-x86_64-GenericCloud.qcow2":"https://cloud.centos.org/centos/7/images/")
for image in "${!IMAGES[@]}" ; do
    echo "$image ${IMAGES[$image]}"
done
