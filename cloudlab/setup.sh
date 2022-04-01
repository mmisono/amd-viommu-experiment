#!/bin/bash -eu

eval `ssh-agent -s`
ssh-add ${SSHKEY}

echo "HOST: $SERVER"
ssh -p ${PORT} ${SERVER} -i ${SSHKEY} << 'ENDSSH'

sudo apt update
sudo apt upgrade -y
sudo apt install -y zsh vim git tmux python3-pip
sudo python3 -m pip install fire numpy

ENDSSH

if [ -f "./setup_secret.sh" ]; then
   . ./setup_secret.sh
fi

