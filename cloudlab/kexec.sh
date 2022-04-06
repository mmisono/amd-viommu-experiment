#! /bin/bash

VERSION=${VERSION:-5.17.0}

CMDLINE="BOOT_IMAGE=/boot/vmlinuz-${VERSION} `cat /proc/cmdline | cut -d' ' -f2-`"
CMDLINE="${CMDLINE} iommu=nopt iommu.strict=1"

echo $CMDLINE

/sbin/kexec -l /boot/vmlinuz-${VERSION} --initrd=/boot/initrd.img-${VERSION} --command-line=${CMDLINE}

/sbin/kexec -e

