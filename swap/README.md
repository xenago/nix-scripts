# swap

Manage swap space/swap files.

## Create a swapfile

A swap file can be more easily managed than a partition, but has more overhead.

### Generate a valid swap file

    sudo fallocate -l 4G /swap.img
    sudo chmod 600 /swap.img
    sudo mkswap /swap.img

### Add file to fstab

    sudo nano /etc/fstab
    /swap.img swap swap defaults 0 0

### Activate swapfile

    sudo swapon -a
    sudo swapon -s

