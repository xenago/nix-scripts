# disk-serials

  Display the serial numbers of disks in the system.

## lsblk method

    lsblk -o NAME,SERIAL

## hdparm method

Install `hdparm`, e.g.

    sudo apt-get install -y hdparm

Run the shell command:

    sudo hdparm -I /dev/sd? |& grep -E 'Serial Number|/dev'

Note that this command discards errors so some disks might not show up.
