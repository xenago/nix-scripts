# ceph

Control and manage the Ceph storage system.

# General Commands

Ceph status:

    ceph -s

Ceph health:

    ceph health detail

# CephFS

Commands and processes related to the Ceph File System.

## Deleting a Ceph File System

1. Disconnect all clients and ensure data has been migrated and both the data and metadata pools for the filesystem have been completely emptied. This is not techincally necessary, but will ensure that all the data has been dealt with.

2. Set the filesystem as 'down' and wait for all MDSes for the filesystem to become standbys.

        ceph fs set <cephfs_name> down true

3. The 'down' command is non-blocking but is generally slow. Once the MDSes for the filesystem are all no longer available, the filesystem can be deleted.

        ceph fs rm <cephfs_name> --yes-i-really-mean-it

4. Remove the <cephfs_name>.mds service (this can be done in the dashboard).

5. Check for leftover CRUSH rules - if the only pool(s) using the rule are being deleted, make note of the rule names so they can be removed from the crushmap after the pools are deleted.

        ceph osd dump | grep "^pool" | grep "crush_rule "

6. Proceed to delete the data and metadata pools. First, allow pool deletion by setting `mon_allow_pool_delete` to true in the config (this can be done in the dashboard). Then, delete the pools (yes this command is weird, but it's done intentionally):

        ceph osd pool delete <cephfs_name_data> <cephfs_name_data> --yes-i-really-really-mean-it
        ceph osd pool delete <cephfs_name_metadata> <cephfs_name_metadata> --yes-i-really-really-mean-it

7. (Optional) Now that the pools are deleted, remove the unnecessary crushmap rules: 

        cephadm shell --mount /home/<username> -- ceph osd getcrushmap -o /mnt/<username>/crushmap.compiled
        <note the number>
        cephadm shell --mount /home/<username> -- crushtool -d /mnt/<username>/crushmap.compiled -o /mnt/<username>/crushmap.text
        sudo nano ~/crushmap.text
        <remove the rule(s) and save>
        cephadm shell --mount /home/<username> -- crushtool -c /mnt/<username>/crushmap.text -o /mnt/<username>/crushmap.compiled.new
        cephadm shell --mount /home/<username> -- ceph osd setcrushmap -i /mnt/<username>/crushmap.compiled.new
        <expect the previously-noted number to have incremented by 1>

8. If you created users with permissions for pool(s) that no longer exist, delete them or edit their permissions:

        ceph auth ls | grep -C 5 <pool_name>
        ceph auth del <obsolete-username>
        ceph auth caps <read-only-username> mds 'allow r path=/' mon 'allow r' osd 'allow r tag cephfs data=cephfs2_metadata, allow r pool=cephfs2_data'
        ceph auth caps <read-write-username> mds 'allow r path=/, allow rw path=/Media, allow rw path=/Share' mon 'allow r' osd 'allow rw tag cephfs data=cephfs2_metadata, allow rw pool=cephfs2_data'
