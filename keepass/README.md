# keepass

Related to the use of `KeePass`.

## `KeeWeb`

This is generally the most useful cross-platform KeePass client, even though it is not really maintained currently. Use of [containerized `KeeWeb`](https://hub.docker.com/r/antelle/keeweb) that is [useful alongside `WebDAV`](../webdav). Although [other versions](https://github.com/keeweb/keeweb) are available as well, self-hosting is preferable.

1. Add or create based on [`keeweb-docker-compose.yml`](keeweb-docker-compose.yml)

2. If being exposed publicly, use a reverse proxy to encrypt the traffic. See the notes regarding the configuration. A sample nginx config is available: ([`keeweb.nginx.conf`](keeweb.nginx.conf))

3. If using with WebDav, it may be required to change the Save method in the Storage section of the KeeWeb Settings to `Overwrite the kdbx file with PUT`.
