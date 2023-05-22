# write-cache

Control disk write cache behaviour.

## Useful commands:

List block devices:

    ls /sys/block

Check how the system treats the device (`write through` = no cache, `write back` = cache flushes required):

    cat /sys/block/$blockDev/queue/write_cache

![image](https://github.com/xenago/nix-scripts/assets/11216007/0b26d200-da20-4c6f-8d13-32dd10961c27)

  * Note: the default value here does not necessarily represent the actual hardware capabilities, and can be unsafe to change manually
  * However, it is *possible* to change this value, e.g. `echo "write through" > /sys/block/$blockDev/queue/write_cache`

### General commands for traditional block devices

Check if write-caching is supported:

    hdparm -W /dev

Disable write-caching:

    hdparm -W 0 /dev/$blockDev

Enable write-caching:

    hdparm -W 1 /dev/$blockDev

### NVMe-specific commands

Check if `vwc` (Volatile Write Cache) is supported on NVMe devices:

    nvme id-ctrl /dev/$blockDev | grep 'vwc '

* Note: it seems like anything other than 0 for this parameter means that the feature is not required or supported (for example, with Optane)

If `vwc` is supported, check if it is enabled:

    nvme get-feature -f 6 /dev/$blockDev

Disable `vwc`:

    nvme set-feature -f 6 -v 0 /dev/$blockDev

Enable `vwc`:

    nvme set-feature -f 6 -v 1 /dev/$blockDev
