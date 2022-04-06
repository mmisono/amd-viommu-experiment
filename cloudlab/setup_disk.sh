#!/bin/bash -eu

# based on https://github.com/opencord/automation-tools/blob/master/scripts/cloudlab-disksetup.sh

# Don't do anything if not a CloudLab node
[ ! -d /usr/local/etc/emulab ] && exit 0

# The watchdog will sometimes reset groups, turn it off
# if [ -e /usr/local/etc/emulab/watchdog ]; then
#     echo "Disable watchdog"
#     sudo /usr/bin/perl -w /usr/local/etc/emulab/watchdog stop
#     sudo mv /usr/local/etc/emulab/watchdog /usr/local/etc/emulab/watchdog-disabled
# fi


# Mount extra space, if haven't already
if [ ! -d /mnt/extra ]; then
    sudo mkdir -p /mnt/extra
    sudo chmod 777 /mnt/extra

    if [ -e /usr/testbed/bin/mkextrafs ] && [ -b /dev/sdb ]; then
        if [ ! -b /dev/sdb1 ]; then
            # Sometimes this command fails on the first try
            sudo /usr/testbed/bin/mkextrafs -s 1 -r /dev/sdb -qf "/mnt/extra/" || sudo /usr/testbed/bin/mkextrafs -s 1 -r /dev/sdb -qf "/mnt/extra/"
        else
            echo "/dev/sdb1 /mnt/extra/ ext4 defaults 0 0" | sudo tee -a /etc/fstab
        fi
        sudo mount -a
        # Check that the mount succeeded (sometimes mkextrafs succeeds but device not mounted)
        mount | grep sdb || (echo "ERROR: mount failed, exiting!" && exit 1)
    else
        echo "No disk found!"
    fi
fi
