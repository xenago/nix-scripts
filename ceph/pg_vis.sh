#! /bin/bash

# Command dependencies:
# * ceph (provided by ceph-common package)
# * jq

# Description:
# Useful script to sanity-check placement of data on hosts
# Modified to adjust formatting and take in the input argument for pool name

# Attribution:
# Entirely based on a script posted by Bryan Stillwell on the Ceph Mailing list
# Thread: "CRUSH rule for EC 6+2 on 6-node cluster"
# Link: https://www.mail-archive.com/ceph-users@ceph.io/msg10289.html

# Instructions:
# Include the name of the pool as the argument when running, e.g.
# ./pg_vis.sh pool_name
# Output should look something like this:
# Displaying pg placement for pool: cephfs2_metadata
# 6.0
#       1 stor1
#       1 stor2
#       1 stor3
# 6.1
#       1 stor1
#       1 stor2
#       1 stor4
# ...
# In that example, the pool was 3xreplicated and 4 servers are available for placement.
# Thus it appears the rules are working as expected - 1 copy each, on 3 randomly-selected servers.

echo "Displaying pg placement by host for pool: $1"
for pg in $(ceph pg ls-by-pool $1 -f json | jq -r '.pg_stats[].pgid'); do
 echo $pg
 for osd in $(ceph pg map $pg -f json | jq -r '.up[]'); do
   ceph osd find $osd | jq -r '.host'
 done | sort | uniq -c | sort -n -k1
done
