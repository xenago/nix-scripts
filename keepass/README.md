# keepass

Related to the use of `KeePass`, an open standard for password storage. KeePass is particularly useful when paired with [`WebDAV`](../webdav) for remote storage of the password database.

## `KeePass2Android`

[KeePass2Android](https://play.google.com/store/apps/details?id=keepass2android.keepass2android) is the most useful Android client compatible with KeePass databases.

## `KeeWeb`

This is generally the most useful cross-platform KeePass client, even though it is not really maintained currently.

These steps cover the [containerized hosting](https://hub.docker.com/r/antelle/keeweb) of [`KeeWeb`](https://github.com/keeweb/keeweb) - it can be used via other means as well, such as the desktop app.

1. Add or create based on [`keeweb-docker-compose.yml`](keeweb-docker-compose.yml)

2. If being exposed publicly, use a reverse proxy to encrypt the traffic. See the notes regarding the configuration. A sample nginx config is available: ([`keeweb.nginx.conf`](keeweb.nginx.conf))

3. If using with WebDav, it may be required to change the Save method in the Storage section of the KeeWeb Settings to `Overwrite the kdbx file with PUT`.
