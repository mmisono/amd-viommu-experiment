#!/bin/bash -eu

if [ -z ${NAME+x} ]; then
    echo "Please set \$NAME";
    exit
fi

if [ -z ${USER+x} ]; then
    echo "Please set \$USER";
    exit
fi

PORT=22
SERVER=${USER}@${NAME}.utah.cloudlab.us
SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
KEY=${SCRIPTDIR}/id_rsa

eval `ssh-agent -s`
ssh-add ${KEY}

echo "HOST: $SERVER"
ssh -p ${PORT} ${SERVER} -i ${KEY} <<'ENDSSH'

sudo apt update
sudo apt upgrade -y
sudo apt install -y zsh vim git python3-pip
sudo python3 -m pip install fire numpy

ENDSSH
