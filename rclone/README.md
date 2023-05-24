# rclone

Usage of rclone for interaction with remote storage.

## Basic usage with Dropbox

The idea is to create a regular rclone API connection to Dropbox, and then another rclone connection on top of that with encryption enabled.
This will permit uploading and downloading encrypted files which are only readable easily using rclone.
The assumption is that a mountpoint will then be created which exposes the files via a filesystem interface.

Note: headless Ubuntu or Debian is assumed but should work similarly anywhere.

### Installation and basic setup

1. Install rclone:

       sudo su
       curl https://rclone.org/install.sh | bash
       exit

2. On server, create a config for dropbox:

       rclone config
         > select option 13 for dropbox

3. On machine with web browser and rclone:

       rclone authorize dropbox

    Follow that process to authorize; enter the provided code into rclone on the server.

4. Then, run rclone config again and create a crypt, option 14. I recommend creating a subfolder in the dropbox web ui in which to contain your encrypted data.

    Then in the crypt remote, use the name of the folder you created, e.g.:

       dropbox:foldername

    Set the password and salt, save in your key store/password manager.

5. At this point, it is possible to copy files to and from the remote.

   For example, this will create a folder called `myfiles` in the encrypted drive:
  
       rclone mkdir dropbox_crypt:myfiles
  
   Upload `file.txt` into the newly-created folder:

       rclone copy -P /path/to/my/file.txt dropbox_crypt:myfiles

   Download `file.txt` from the remote location:
  
       rclone copy -P /path/to/my/file.txt dropbox_crypt:myfiles

### Mounting

1. Create a mountpoint folder, e.g. `/mnt/dropbox_crypt`:

       sudo mkdir /mnt/dropbox_crypt

2. Make a note of your `uid` and `gid` numbers to ensure that when it is mounted, your user will be the owner of the files (only necessary for writing, not for read-only):

       id <username>

3. To persist the mountpoint, create a service:

       sudo nano /lib/systemd/system/rclonemount.service

   Make sure to look closely and edit as appropriate:

       [Unit]
       Description=Rclone Mount for Dropbox Crypt
       AssertPathIsDirectory=/mnt/dropbox_crypt

       [Service]
       Type=simple
       ExecStart=/usr/bin/rclone mount \
              --config=/home/<username>/.config/rclone/rclone.conf \
              --allow-other \
              --gid=1000 \
              --uid=1000 \
              --log-level=INFO \
              --vfs-cache-mode=off \
              --vfs-read-chunk-size=64M \
              --vfs-read-chunk-size-limit=4G \
              --dir-cache-time=5m0s \
              --tpslimit=10 \
              --bwlimit=60M \
              --rc \
              --rc-web-gui \
              --rc-addr=<local-ip>:5572 \
              --rc-user=me \
              --rc-pass=pass \
              --rc-serve \
              dropbox_crypt: /mnt/dropbox_crypt
       ExecStop=/bin/fusermount -u /mnt/dropbox_crypt
       Restart=always
       RestartSec=10

       [Install]
       WantedBy=default.target

    Notes:

      * Set the config path to the one created when `rclone config` was run
      * `--allow-other` enables other users to access (generally, read) the mounted disk
      * Set the `gid` and `uid` to match your user account and ensure write access (see previous step)
      * Cache is off in this example - files are uploaded without taking up space on the actual disk, but if uploads fail they won't be retried since they are uncached
      * Set `--vfs-cache-mode=writes` instead of `off` for proper full read-write access to the disk (like Google Drive desktop) but this will consume local disk space for files until they are uploaded
      * Set `tpslimit` to control the number of api calls/queries per second
      * Set `bwlimit` to control the max permitted bandwidth
      * Set `dir-cache-time` to control how long rclone will assume the contents of a directory are valid after last access
      * The remote control web gui is enabled, either set the correct local IP or remove all the `--rc*` arguments
      * Add `--read-only` to use the mountpoint only for consumption and not uploading

4. Set up and activate the service:

       sudo systemctl daemon-reload
       sudo systemctl enable --now rclonemount

5. Check that you can view and read the files:

       ls /mnt/dropbox_crypt
