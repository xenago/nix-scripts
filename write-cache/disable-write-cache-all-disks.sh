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
        # Check if it is supported
        if [[ "$(hdparm -W /dev/$blockDev)" != *"not supported"* ]]; then
            hdparm -W 0 /dev/$blockDev
        else
            echo "$(hdparm -W /dev/$blockDev)"
        fi
    # Try a different method with nvme devices
    elif [[ "$blockDev" == "nvme"* ]]; then
        # Check if the device has the 'vwc ' feature (the space filters out other features)
        if [[ "$(sudo nvme id-ctrl /dev/$blockDev | grep 'vwc ' | sed 's/[^0-9]*//g')" != "0" ]]; then
            # vwc seems available, so try to disable the feature
            vwcResult=$(nvme set-feature -f 6 -v 0 /dev/$blockDev 2>&1)
            # It's possible that the feature needs to be disabled one level up (e.g. nvme0 instead of nvme0n1)
            if [[ "$vwcResult" == *"FEATURE_NOT_PER_NS"* ]]; then
                # Try to disable on the entire namespace
                fullDev=$(echo $blockDev | sed 's/n[0-9]\+//g')
                echo && echo /dev/$fullDev
                nvme set-feature -f 6 -v 0 /dev/$fullDev
            else
                # Format the result similar to hdparm for consistency
                echo && echo /dev/$blockDev:
                echo "$vwcResult"
            fi
        else
            echo && echo /dev/$blockDev:
            echo " Volatile Write Cache not present"
        fi
        echo " write_cache: $(cat /sys/block/$blockDev/queue/write_cache)"
    fi
done
