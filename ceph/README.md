# ceph

Control and manage the Ceph storage system.

# General Notes

Cephadm is the orchestrator assumed, but native commands can be used in most cases if the `ceph-common` package/tools are installed and sufficient permissions are available (as `root` or with `sudo`, for example).

Cephadm-style `ceph status`:

    sudo cephadm shell ceph -s

Traditional `ceph status`:

    sudo ceph -s

Ceph health:

    ceph health detail

# CephFS

Commands and processes related to the Ceph File System.

## Creating a second Ceph File System

In this example, a 6+2 EC data pool on HDD will be created alongside a 3x replicated metadata pool on SSD.

1. Allow multiple filesystems:

       ceph fs flag set enable_multiple true

2. Create the pools, e.g. `cephfs2_data` and `cephfs2_metadata` in the dashboard with mostly default settings:

    Create pool `cephfs2_data`:
    
       erasure
       pg autoscale on
       ec overwrites on
       cephfs application
       Create new EC profile
           Name ec62_profile
           jerasure
           6,2
           failure domain osd
           reed_sol_van
           2048 packetsize
           default crush root
           hdd class
           Dir /usr/lib64/ceph/erasure-code
       Compression none
       No quotas
	
    Create pool `cephfs2_metadata`:
    
       replicated
       pg autoscale on
       Size 3
       cephfs application
       Use replicated_ssd rule (like replicated but restricted to ssds)
           If you need to create it, use this command:
           cephadm shell ceph osd crush rule create-replicated replicated_ssd default host ssd
       No compression
       No quotas

3. Edit the crushmap to add customization that ensures 2 pieces of data are stored on each of 4 different servers (6+2=8, 8/2=4) thus allowing high availability with a minimum of hardware.

    Grab and decompile the crushmap:

       sudo cephadm shell --mount /home/<username> -- ceph osd getcrushmap -o /mnt/<username>/crushmap.compiled
       sudo cephadm shell --mount /home/<username> -- crushtool -d /mnt/<username>/crushmap.compiled -o /mnt/<username>/crushmap.text
       sudo nano ~/crushmap.text
        
    Edit the `cephfs2` profile to fit like the following:
        
       rule cephfs2_data {
               id xxxxx
               type erasure
               min_size 6
               max_size 8
               step set_chooseleaf_tries 5
               step set_choose_tries 100
               step take default class hdd
               step choose indep 4 type host
               step choose indep 2 type osd
               step emit
       }
    
    Compile and import the modified crushmap:
    
       sudo cephadm shell --mount /home/<username> -- crushtool -c /mnt/<username>/crushmap.text -o /mnt/<username>/crushmap.compiled.new
       sudo cephadm shell --mount /home/<username> -- ceph osd setcrushmap -i /mnt/<username>/crushmap.compiled.new

    **NOTE:** min_size is set to 4 in the actual pool, seems to be more reliable when one server goes down... This shouldn't matter since a "pool min_size must be between" error is thrown if set lower, not sure what the deal is with that.

4. Create the filesystem and 2 MDS (one for standby):

       ceph fs new cephfs2 cephfs2_metadata cephfs2_data --force
       ceph orch apply mds cephfs2 --placement="2"

5. Set the estimated size to help the autoscaler, e.g. 250 terabytes:

       ceph osd pool set cephfs2_data target_size_bytes 250T

6. Authorize users for the new pool, retaining existing permissions:

       ceph auth caps client.<read-only-username> mds 'allow r path=/' mon 'allow r' osd 'allow r tag cephfs data=cephfs_metadata, allow r pool=cephfs_data, allow r tag cephfs data=cephfs2_metadata, allow r pool=cephfs2_data'
       ceph auth caps client.<read-write-username> mds 'allow r path=/, allow rw path=/Media, allow rw path=/Share' mon 'allow r' osd 'allow rw tag cephfs data=cephfs_metadata, allow rw pool=cephfs_data, allow rw tag cephfs data=cephfs2_metadata, allow rw pool=cephfs2_data'

7. (Optional - not recommended) Change the default filesystem from the existing one to the new one:

       ceph fs set-default cephfs2

8. Create a kernel mount on a client device:

       sudo mkdir /mnt/cephfs2

    Add additional mounts in fstab, e.g.:

       :/ /mnt/cephfs2 ceph name=ruser,mds_namespace=cephfs2 0 0

    Mount it:

       sudo mount /mnt/cephfs2

9. Using the admin user, mount and create paths for users, then chown for them to allow access.

    Create a directory for mounting:
    
       mkdir /home/<username>/cephmnt
    
    Mount the filesystem:

       sudo mount -t ceph :/ /home/noah/cephmnt -o name=admin,mds_namespace=cephfs2

    Note: can also use fstab to mount, e.g.
    
       sudo nano /etc/fstab
       :/ /home/<username>/cephmnt ceph     name=admin 0 0
       sudo mount /home/<username>cephmnt
    
    Create the necessary paths, e.g.:
    
       mkdir /home/<username>/cephmnt/Media
       sudo chown -R username:username /home/<username>/<username>/Media

## Deleting a Ceph File System

1. Disconnect all clients and ensure data has been migrated and both the data and metadata pools for the filesystem have been completely emptied. This is not techincally necessary, but will ensure that all the data has been dealt with.

2. Set the filesystem as `down` and wait for all MDSes for the filesystem to become standbys.

       ceph fs set <cephfs_name> down true

3. The `down` command is non-blocking but is generally slow. Once the MDSes for the filesystem are all no longer available, the filesystem can be deleted.

       ceph fs rm <cephfs_name> --yes-i-really-mean-it

4. Remove the `<cephfs_name>.mds` service (this can be done in the dashboard).

5. Check for leftover CRUSH rules - if the only pool(s) using the rule are being deleted, make note of the rule names so they can be removed from the crushmap after the pools are deleted.

       ceph osd dump | grep "^pool" | grep "crush_rule "

6. Proceed to delete the data and metadata pools. First, allow pool deletion by setting `mon_allow_pool_delete` to true in the config (this can be done in the dashboard). Then, delete the pools (yes this command is weird, but it's done intentionally):

       ceph osd pool delete <cephfs_name_data> <cephfs_name_data> --yes-i-really-really-mean-it
       ceph osd pool delete <cephfs_name_metadata> <cephfs_name_metadata> --yes-i-really-really-mean-it

7. (Optional) Now that the pools are deleted, remove the unnecessary crushmap rules: 

       sudo cephadm shell --mount /home/<username> -- ceph osd getcrushmap -o /mnt/<username>/crushmap.compiled
       sudo cephadm shell --mount /home/<username> -- crushtool -d /mnt/<username>/crushmap.compiled -o /mnt/<username>/crushmap.text
       sudo nano ~/crushmap.text
	
    Remove the rule(s) and save, then recompile and import:
	
       cephadm shell --mount /home/<username> -- crushtool -c /mnt/<username>/crushmap.text -o /mnt/<username>/crushmap.compiled.new
       cephadm shell --mount /home/<username> -- ceph osd setcrushmap -i /mnt/<username>/crushmap.compiled.new

8. If you created users with permissions for pool(s) that no longer exist, delete them or edit their permissions:

       ceph auth ls | grep -C 5 <pool_name>
       ceph auth del client.<obsolete-username>
       ceph auth caps client.<read-only-username> mds 'allow r path=/' mon 'allow r' osd 'allow r tag cephfs data=cephfs2_metadata, allow r pool=cephfs2_data'
       ceph auth caps client.<read-write-username> mds 'allow r path=/, allow rw path=/Media, allow rw path=/Share' mon 'allow r' osd 'allow rw tag cephfs data=cephfs2_metadata, allow rw pool=cephfs2_data'

9. (Optional) If the default file system was deleted, change it to the remaining one:

       ceph fs set-default cephfs2
