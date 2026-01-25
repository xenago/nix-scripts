# sudo

Manage superusers.

## sudoers configuration

Many distros include the directive `%sudo ALL=(ALL:ALL) ALL` to allow members of the group `sudo` to run commands as `root`.

In that scenario, it is enough to add the specific user to the aforementioned group:

    usermod -aG sudo <username>

Futher, most distros' `/etc/sudoers` configuration has the directive `@includedir /etc/sudoers.d` which will incorporate additional config files automatically if they exist.

In that case, this one-liner will grant that group passwordless sudo access.
    
    sudo bash -c 'echo "%sudo ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers.d/passwordless-sudo'
