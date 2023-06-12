# vpn

Related to the use of VPNs.

## AirVPN with Gluetun

Usage of [AirVPN](https://airvpn.org/) with [Gluetun](https://github.com/qdm12/gluetun/wiki/AirVPN), to be accessed by [other containers](https://github.com/qdm12/gluetun/wiki/Connect-a-container-to-gluetun) with a forwarded port for use with e.g. [P2P software](https://hub.docker.com/r/linuxserver/qbittorrent).

### Steps:

1. Using the AirVPN website, create a device mapping
2. Use the config generator to acquire WireGuard keys and IP range for the device
3. Map forwarded ports to the device using the AirVPN website
4. Use the `docker-compose-gluetun-airvpn.yml` config, but with necessary changes:

    1. Provided keys
    2. Provided IP range(s) (remove IPv4 or IPv6 if both are not being used by WireGuard)
    3. Internal forwarded ports (i.e. forward some ports you want to access on the docker host directly, such as a local Web UI for a P2P client)
    4. Optional environment variables:

           SERVER_COUNTRIES: Comma separated list of countries
           SERVER_REGIONS: Comma separated list of regions
           SERVER_CITIES: Comma separated list of cities
           SERVER_NAMES: Comma separated list of server names
           SERVER_HOSTNAMES: Comma separated list of server hostnames

6. To connect a container, add line to compose config: `network_mode: "service:gluetun"`
7. To access a port on a container from within the gluetun network, use the gluetun container hostname, e.g. `gluetun:8080`
8. To validate IP in VPN container, it is convenient to use a third party service with the included `wget` binary, e.g. `sudo docker exec -it gluetun wget -qO- ifconfig.io`
9. To validate IP in a client container, sometimes `curl` is available instead, e.g. `sudo docker exec -ti qbittorrent curl ifconfig.io`
