# pci

Info related to PCIe devices.

## Useful commands:

List PCIe devices (root required for useful info):

    sudo lspci -vv

Trim most info and just [check the link speed](https://unix.stackexchange.com/a/193340):
  
    sudo lspci -vv | grep -P "[0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f]|LnkSta:"

