#!/bin/bash -eu

eval `ssh-agent -s`
ssh-add ${SSHKEY}

echo "HOST: $SERVER"

scp -P ${PORT} -i ${SSHKEY} -- ./setup_disk.sh \
                               ./kexec.sh \
                               ./build_linux.sh \
                               ./linux_config_v5.17 \
                               ./grub \
                               ${SERVER}:

ssh -p ${PORT} ${SERVER} -i ${SSHKEY} << 'EOF'
sudo apt update
sudo apt upgrade -y
sudo apt install -y tig zsh vim git tmux hwloc \
                    libelf-dev libssl-dev dwarves \
                    python3-pip python3-venv \
                    bear clangd clang-format \
                    ripgrep kexec-tools
sudo python3 -m pip install fire numpy yapf

bash setup_disk.sh
cd /mnt/extra
cp $HOME/build_linux.sh .
bash build_linux.sh
sudo cp /etc/default/grub /etc/default/grub.backup
sudo cp $HOME/grub /etc/default/grub
sudo update-grub2
EOF


if [ -f "./setup_secret.sh" ]; then
   . ./setup_secret.sh
fi

