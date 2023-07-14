# webdav

Related to the use of `WebDAV`.

## `nginx-webdav-nononsense`

Use of [containerized `nginx`](https://hub.docker.com/r/dgraziotin/nginx-webdav-nononsense) that is [preconfigured for `WebDAV`](https://github.com/dgraziotin/docker-nginx-webdav-nononsense).

1. Create/determine folders for shared data

    * The container automatically shares whatever is located in the `/data` directory, so create a folder to share if you don't already have one in mind

          mkdir -p <path>/webdav/data

    * If using with a reverse proxy as is highly recommended, creating a [configuration file](https://github.com/dgraziotin/docker-nginx-webdav-nononsense/issues/26) is generally required for it to [work properly](https://github.com/dgraziotin/docker-nginx-webdav-nononsense/issues/25#issuecomment-1055484956). Make sure to set the IP of your proxy server in CIDR format!

          mkdir -p <path>/webdav/config/nginx
          nano <path>/webdav/config/nginx/server.conf

       Contents:

          set_real_ip_from  123.123.123.123/32;
          real_ip_header    X-Forwarded-For;
          real_ip_recursive on;
      
2. Add or create based on [`webdav-docker-compose.yml`](webdav-docker-compose.yml)

3. If being exposed publicly, use a reverse proxy to encrypt the traffic. See the notes above regarding the configuration. A sample nginx config is available: ([`webdav.nginx.conf`](webdav.nginx.conf))
