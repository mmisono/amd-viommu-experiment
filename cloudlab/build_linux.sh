#!/bin/bash -eu

if [ ! -d linux ]; then
    git clone --depth 1 --branch v5.17 https://github.com/torvalds/linux
fi
mkdir -p linux/out
cd linux
cp ~/linux_config_v5.17 out/.config
bear make O=out -j$(nproc)
sudo make O=out INSTALL_MODE_STRIP=1 modules_install
sudo make O=out install
