#!/bin/bash

# Command dependencies:
# * sudo (if not root)
# * hdparm (for most block devices)
# * nvme (if any nvme are present, provided by nvme-cli package)
# * sed (if any nvme are present)

# If not root, become root (retaining environment variables)
if [[ "$EUID" -ne 0 ]]; then
    exec sudo -E "$0" "$@"
fi

# Iterate through block devices
for blockDev in $(ls /sys/block)
do
    # Ignore devices which are unlikely to support the hdparm command
    if [[ "$blockDev" != "dm-"* && "$blockDev" != "loop"* && "$blockDev" != "md"* && "$blockDev" != "nvme"* ]]; then
        hdparm -W /dev/$blockDev
    # Try a different method with nvme devices
    elif [[ "$blockDev" == "nvme"* ]]; then
        # Format the result similar to hdparm for consistency
        echo && echo /dev/$blockDev:
        # Check if the device has the 'vwc ' feature (the space filters out other features)
        if [[ "$(sudo nvme id-ctrl /dev/$blockDev | grep 'vwc ' | sed 's/[^0-9]*//g')" != "0" ]]; then
            # vwc seems available, so check for the status of the feature
            echo " $(nvme get-feature -f 6 /dev/$blockDev)"
        else
            echo " Volatile Write Cache not present"
        fi
        echo " write_cache: $(cat /sys/block/$blockDev/queue/write_cache)"
    fi
done
