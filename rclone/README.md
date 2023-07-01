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

5. At this point, it is possible to copy files to and from the remote. Due to [Dropbox limitations](https://help.dropbox.com/organize/file-names), with rclone encryption file/folder names must not exceed [143 characters](https://forum.rclone.org/t/problem-with-deep-paths-dropbox/14822/3) in length.

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
              --tpslimit-burst=20 \
              --bwlimit=120M \
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
      * Set `--vfs-cache-mode=writes` instead of `off` for proper full read-write access to the disk (like Google Drive desktopdoes) - this will rectify file access issues but consume local disk space for files until they are closed or uploaded
        * There are ways to limit this, like `vfs-cache-max-size`, but they are imperfect
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

## Syncing between providers (e.g. Google Drive to Dropbox)

Note: it is recommended to use the Google Cloud console to create a Drive API project in order to get OAuth credentials for use with rclone

1. Create rclone config entries for the providers in use. In this example, I will sync from a plaintext Google Drive remote called `gsuite` to an encrypted Dropbox called `dropbox_crypt`.

2. Determine if syncing or copying to the destination, since there are tradeoffs between either option.

3. Determine [parameters](https://rclone.org/flags/) to use depending on needs:

    * `--buffer-size=64Mi`
      * Amount to buffer files read when transferring (default 16Mi)
    * `--bwlimit=120M`
      * Control bandwidth usage
    * `--ignore-existing`
      * Do not copy files if they already exist on the destination
    * `--progress`
      * Track the transfer in real time
    * `--size-only`
      * Compare using file size rather than checksum
    * `--tpslimit=3 --tpslimit-burst=3`
      * Limit how hard the APIs/filesystem will be hit every second (default 1)
    * `--transfers=3`
      * Set the number of files to be worked on in parallel (default 4)
    * `--update`
      * Skip files that are newer on the destination
    * `--verbose`
      * Show some debug info

4. Perform a dry run

       rclone copy --progress --verbose --dry-run "gsuite:sourcepath" "dropbox_crypt:destpath"

5. If connected over ssh, it is recommended to run the actual sync inside a tool like `tmux` or `screen` to avoid disconnections killing the transfer, but that is optional:

       rclone copy -P -v --tpslimit=10 --bwlimit=120M --size-only --dry-run "gsuite:sourcepath" "dropbox_crypt:destpath"
