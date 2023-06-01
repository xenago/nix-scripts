# p2p

Related to the use of P2P software like Bittorrent.

## qBittorrent

Use of [containerized lsio qBittorrent](https://hub.docker.com/r/linuxserver/sabnzbd) with optional [VPN provider integration](../vpn) (using a service with port-forwarding support, such as AirVPN).

1. Create folders for volume data

    * Using a shared folder as the main volume root for downloaded files is [recommended](https://wiki.servarr.com/docker-guide#consistent-and-well-planned-paths), to enable efficient movement of files by different trusted containers

          mkdir -p <path>/qbittorrent/config
          mkdir -p <path>/shared/torrent

2. Add or create based on [`qbittorrent-docker-compose.yml`](qbittorrent-docker-compose.yml)

    * Make sure to use a recent, updated container release
    * If used with a VPN container, then set it in the compose file, e.g. `network_mode: "service:gluetun"`
    * If used with a VPN and the Web UI/API is being used, then forward that port at the VPN container instead

3. Forward a port (e.g. TCP 6881) to the container for use with Bittorrent

  * If used with a VPN, the service should support port-forwarding and that should be configured with your VPN service provider and in your VPN client
  * If not used with a VPN, forward the port in your router or firewall

4. Sign in with `admin`/`adminadmin` and set the config options as you prefer. A list of aditional trackers is available at https://github.com/ngosang/trackerslist if desired.
   Here are some configuration options to consider (see e.g. `qbittorrent/config/qBittorrent/qBittorrent.conf`):

       [AutoRun]
       enabled=false
       program=

       [BitTorrent]
       Session\AddTrackersEnabled=true
       Session\AdditionalTrackers=udp://tracker.opentrackr.org:1337/announce\n\nhttp://tracker.opentrackr.org:1337/announce
       Session\AsyncIOThreadsCount=12
       Session\CheckingMemUsageSize=256
       Session\DefaultSavePath=/shared/torrent/complete/
       Session\GlobalDLSpeedLimit=20000
       Session\GlobalUPSpeedLimit=10000
       Session\HashingThreadsCount=2
       Session\IgnoreLimitsOnLAN=true
       Session\IgnoreSlowTorrentsForQueueing=true
       Session\MaxActiveDownloads=10
       Session\MaxActiveTorrents=25
       Session\MaxActiveUploads=10
       Session\MaxConnections=2048
       Session\MaxConnectionsPerTorrent=1024
       Session\MaxUploads=64
       Session\MaxUploadsPerTorrent=32
       Session\Port=6881
       Session\QueueingSystemEnabled=true
       Session\SlowTorrentsDownloadRate=25
       Session\SlowTorrentsUploadRate=25
       Session\TempPath=/shared/torrent/incomplete/
       Session\TempPathEnabled=true
       Session\TorrentExportDirectory=/shared/torrent/backup/
       
       [Core]
       AutoDeleteAddedTorrentFile=Never
       
       [LegalNotice]
       Accepted=true

       [Meta]
       MigrationVersion=3

       [Network]
       PortForwardingEnabled=false
       Proxy\OnlyForTorrents=false

       [Preferences]
       Advanced\RecheckOnCompletion=false
       Connection\PortRangeMin=6881
       Connection\ResolvePeerCountries=true
       Connection\UPnP=false
       Downloads\SavePath=/downloads/
       Downloads\TempPath=/downloads/incomplete/
       WebUI\Address=*
       WebUI\AlternativeUIEnabled=false
       WebUI\AuthSubnetWhitelist=192.168.1.0/24, " 192.168.2.0/24", " 172.0.0.0/8"
       WebUI\AuthSubnetWhitelistEnabled=true
       WebUI\BanDuration=3600
       WebUI\CSRFProtection=true
       WebUI\ClickjackingProtection=true
       WebUI\HostHeaderValidation=true
       WebUI\LocalHostAuth=true
       WebUI\MaxAuthenticationFailCount=5
       WebUI\Port=8181
       WebUI\ReverseProxySupportEnabled=true
       WebUI\SecureCookie=true
       WebUI\ServerDomains=*
       WebUI\SessionTimeout=3600
       WebUI\TrustedReverseProxiesList=192.168.1.19
       WebUI\Username=admin

       [SearchEngines]
       disabledEngines=eztv, limetorrents, torlock

6. If the Web UI/HTTP port is being used, use a reverse proxy to encrypt the traffic. A sample nginx config is available: ([`qb.nginx.conf`](qb.nginx.conf))
