# guacamole

Apache Guacamole web-based remote access portal.

## Deployment with Docker

The folder structure on each instance will look like:

```
/srv
|--/guacamole
   |--/compose
   |  |--/docker-compose.yml
   |--/data
      |--<persistent application data>
```

Accordingly, the [docker-compose.yml](docker-compose.yml) file in this repo is structured using relative paths from the `compose` directory into the `data` directory.

This structure has several benefits, including:

* Easier migrations
  * Moving the services to different machines is trivial: the entire `/srv/guacamole` tree can simply be copied to a different location and restarted there
* Automated git-based version management
  * A git repository containing a `docker-compose.yml` file in the root can be cloned directly as the `/srv/guacamole/compose` folder
  * Since the application data is in a different directory, it is safe to overwrite whatever may be in the `compose` folder since the compose file can be easily restored

### Step-by-step containerized deployment

1. Create the application path and download the compose file:

       sudo mkdir -p /srv/guacamole/compose
       sudo chown -R $USER /srv/guacamole/compose
       cd /srv/guacamole/compose
       curl -sLO <url-to-docker-compose.yml>

2. Edit the compose file to add temporary environment variables to the database container to initialize the instance with users, passwords, and a database:

         environment:
           - MARIADB_ROOT_PASSWORD=replace-with-db-root-password-here
           - MARIADB_PASSWORD=replace-with-db-service-account-password-here
           - MARIADB_USER=guacamole_user
           - MARIADB_DATABASE=guacamole_db

3. Start mariadb and watch the logs to see it warm up:

       docker compose -f /srv/guacamole/compose/docker-compose.yml up -d guac-db
       docker compose -f /srv/guacamole/compose/docker-compose.yml logs -f guac-db

4. Run the DB initialization script by piping it from a temporary container into a shell within the persistent database container:

       docker run --rm guacamole/guacamole:<CONTAINER-TAG-VERSION-HERE> /opt/guacamole/bin/initdb.sh --mysql | docker exec -i guac-db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" guacamole_db'



5. Once it has initialized the users and database, remove the environment variable section from the config and start all the containers up:

        docker compose -f /srv/guacamole/compose/docker-compose.yml up -d

6. Once logged in, you can set up RDP and ssh. Use the default credentials `guacadmin / guacadmin`:

        http://<ip-or-host>:8080/guacamole/#/
        
    Note: use `Ctrl+Alt+Shift` to return to the menu.

7. Change the password of the admin user

8. Set up nginx (see `guacamole_site_nginx.conf`), replacing `guacamole.local` with the guacamole IP address or hostname from the perspective of the nginx server, and `guacamole.domain.com` with the domain name used. Make sure to generate certs with e.g. certbot.

### Upgrades

Generally, it is sufficient to bump the version numbers and restart containers with `docker-compose up -d`. However, a full upgrade may require additional steps.

Each [release page](https://guacamole.apache.org/releases/) lists any special requirements in the `Deprecation / Compatibility notes` section. For example, if a database schema upgrade is required, then patch the database as [documented here](https://guacamole.apache.org/doc/gug/mysql-auth.html#upgrading-an-existing-guacamole-database) - see below for details.

#### MariaDB

To upgrade MariaDB to a newer release, add the environment variable `MARIADB_AUTO_UPGRADE=1` to the container and restart it with the newer image tag. Usually, additional upgrade steps are not required, but consult [the documentation](https://mariadb.com/docs/server/server-management/install-and-upgrade-mariadb/upgrading/mariadb-community-server-upgrade-paths) for exact details.

#### Guacamole DB Schema

To update the Guacamole DB Schema, a script must be extracted from the Guacamole release pacakge and run within the database container.

1. Download the latest release file, extract it, and examine the available scripts:

       wget https://dlcdn.apache.org/guacamole/1.6.0/binary/guacamole-auth-jdbc-1.6.0.tar.gz
       tar -xvf guacamole-auth-jdbc-1.6.0.tar.gz
       ls guacamole-auth-jdbc-1.6.0/mysql/schema/upgrade/ -lah

2. If one or more of the scripts is required (for example, upgrading from any previous `1.x` version to `1.6.0`), then run it in a similar way to the initial deployment script with the password set in the environment:

       cat guacamole-auth-jdbc-1.6.0/mysql/schema/upgrade/upgrade-pre-1.6.0.sql | docker exec -i guac-db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" guacamole_db'
