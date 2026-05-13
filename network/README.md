# network

Networking-related.

## Bell Home Hub script

See [`bell_hh_wifi_disable.py`](bell_hh_wifi_disable.py) script alongside this file.

## View list of open ports

`sudo ss -lntup`

## Enable BBR congestion control

BBR enables squeezing better TCP performance out of most connections. This is especially helpful when using software limited by a single connection.

1. Create/edit a sysctl config, e.g.
   ```bash
   sudo nano /etc/sysctl.d/bbr.conf
   ```
   
2. Specify FQ-CoDel queueing algorithm and BBR congestion control
   ```ini
   net.core.default_qdisc=fq_codel
   net.ipv4.tcp_congestion_control=bbr
   ```

3. Apply the config
   ```bash
   sudo sysctl -p /etc/sysctl.d/bbr.conf
   ```

4. Confirm that BBR and FQ-CoDel are active
    ```bash
    sysctl net.ipv4.tcp_congestion_control
    sysctl net.core.default_qdisc
    ```

Note: it is possible to check if `bbr` is supported:
   ```bash
   sysctl net.ipv4.tcp_available_congestion_control
   ```
If `bbr` is not listed, the module can be loaded (though this is usually unnecessary and it will be automatically loaded if required):
   ```bash
   sudo modprobe tcp_bbr
   ```

