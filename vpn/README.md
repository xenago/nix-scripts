# vpn

Related to the use of VPNs.

## OpenVPN

The OpenVPN ecosystem makes it absolutely certain that you won't be able to connect to an older but properly-configured VPN server due to mindless 'security' changes. I'm accessing TLS sites though my VPN, I don't care if the tunnel is `AES-128-CBC` and therefore slightly less private - just let me connect! It's way more secure to allow a valid user into the VPN, than it is to block them thinking that AES isn't secure enough. Availability is a cornerstone of security, this is plain insanity.

### Connecting to a .ovpn file on KDE

1. Install the prerequisites

       sudo apt install network-manager-openvpn

2. Import the VPN file and attempt to connect. You'll likely see it hang endlessly, rather than provide a usable error message.

   Optionally, add the password to the connection. This is insecure.

       sudo nmcli connection modify my-vpn-connection-name-here vpn.secrets 'password=mypasswordhere'

3. Check the logs to see what is breaking, probably a cipher deemed as unsupported by an idiot who hasn't ever operated in the real world:

       OPTIONS ERROR: failed to negotiate cipher with server.  Add the server's cipher ('AES-128-CBC') to --data-ciphers (currently 'AES-256-GCM:AES-128-GCM:CHACHA20-POLY1305') if you want to connect

4. Update the Network Manager config

       ls /etc/NetworkManager/system-connections/
       sudo nano /etc/NetworkManager/system-connections/my-vpn-connection-name-here.nmconnection
 
   Under the `[vpn]` section, add the missing cipher:

       data-ciphers=AES-128-CBC

   Set permissions

       sudo chmod 600 /etc/NetworkManager/system-connections/my-vpn-connection-name-here.nmconnection

5. Reload and connect (using CLI should show errors if any)

       sudo nmcli connection reload
       nmcli connection up "my-vpn-connection-name-here"

## AirVPN with Gluetun

Usage of [AirVPN](https://airvpn.org/) with [Gluetun](https://github.com/qdm12/gluetun/wiki/AirVPN), to be accessed by [other containers](https://github.com/qdm12/gluetun/wiki/Connect-a-container-to-gluetun) with a forwarded port for use with e.g. [P2P software](https://hub.docker.com/r/linuxserver/qbittorrent).

### Steps

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
    * Adding a `depends_on` link to the `gluetun` container is recommended to ensure containers remain functional:
   
          depends_on:
            - gluetun

8. To access a port on a container from within the gluetun network, use the gluetun container hostname, e.g. `gluetun:8080`
9. To validate IP in VPN container, it is convenient to use a third party service with the included `wget` binary, e.g. `sudo docker exec -it gluetun wget -qO- ifconfig.io`
10. To validate IP in a client container, sometimes `curl` is available instead, e.g. `sudo docker exec -ti qbittorrent curl ifconfig.io`

## Self-hosted Headscale

[Headscale](https://earvingad.github.io/posts/headscale/) is a standalone implementation of the Tailscale Wireguard Mesh VPN solution. [Headscale-UI](https://github.com/gurucomputing/headscale-ui) is a frontend for it. Both are deployed with [Docker](https://headscale.net/running-headscale-container/#executing-commands-in-the-debug-container) and require an nginx proxy server.

### Steps

1. Use the `docker-compose-headscale.yml` config as the Docker compose base file.

2. Configure nginx with the template `headscale-nginx.conf`
    * Ensure `server_name` is set to the public DNS hostname of the nginx server
    * Ensure a TLS certificate has been set

Prepare a directory on the host Docker node in your directory of choice, used to hold headscale configuration and the SQLite database:

    mkdir -p /home/<username>/containers/headscale/config
    cd /home/<username>/containers/headscale/config

Create an empty SQlite DB file in the headscale directory:

    touch /home/<username>/containers/headscale/config/db.sqlite

Download a copy of the example configuration from the headscale repository:

    wget -O /home/<username>/containers/headscale/config/config.yaml https://raw.githubusercontent.com/juanfont/headscale/main/config-example.yaml

Open the config file:

    nano /home/<username>/containers/headscale/config/config.yaml

Edit it before starting the container:

    # Override external URL
    server_url: https://headscale.domain.com
    listen_addr: 0.0.0.0:8080
    metrics_listen_addr: 0.0.0.0:9090
    # grpc is optional and not enabled by default, can omit this
    grpc_listen_addr: 0.0.0.0:50443
    # The default /var/lib/headscale path is not writable in the container
    noise:
      private_key_path: /etc/headscale/noise_private.key
    derp:
      private_key_path: /etc/headscale/private.key
    unix_socket: /etc/headscale/headscale.sock
    database.type: sqlite3
    database.sqlite.path: /etc/headscale/db.sqlite

Start it up:

    docker compose -f /home/<username>/containers/headscale/docker-compose.yml up -d

Create an API Key:

    docker exec headscale headscale apikeys create

Login to the UI at `https://headscale.domain.com/web/settings.html`

In the Web UI, create a user and a Preauth Key for the user.

List devices and users to validate:

    docker exec headscale headscale nodes list
    docker exec headscale headscale users list

Permit IP forwarding:

    echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/98-tailscale.conf
    echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/98-tailscale.conf
    sudo sysctl -p /etc/sysctl.d/98-tailscale.conf

Run the client to advertise as an exit node:

    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up --login-server=https://headscale.domain.com --advertise-routes=192.168.1.0/24 --accept-dns=false --accept-routes --advertise-exit-node

Back in the web UI, go to the device and enable the exit node under `Device Routes`.
