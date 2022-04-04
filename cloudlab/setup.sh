#!/bin/bash -eu

eval `ssh-agent -s`
ssh-add ${SSHKEY}

echo "HOST: $SERVER"
ssh -p ${PORT} ${SERVER} -i ${SSHKEY} << 'ENDSSH'

sudo apt update
sudo apt upgrade -y
sudo apt install -y tig zsh vim git tmux hwloc \
                    libelf-dev libssl-dev dwarves \
                    python3-pip python3-venv \
                    bear clangd clang-format
sudo python3 -m pip install fire numpy yapf

ENDSSH

if [ -f "./setup_secret.sh" ]; then
   . ./setup_secret.sh
fi

