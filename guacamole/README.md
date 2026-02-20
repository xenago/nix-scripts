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

4. Once it has initialized the users and database, remove the environment variable section from the config and start it again:

        docker compose -f /srv/guacamole/compose/docker-compose.yml up -d guac-db

5. Run the DB initialization script by piping it from a temporary container into a shell within the persistent database container:

       docker run --rm guacamole/guacamole:<CONTAINER-TAG-VERSION-HERE> /opt/guacamole/bin/initdb.sh --mysql | docker exec -it guac-db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" guacamole_db'

6. Start the other containers up:

        docker compose -f /srv/guacamole/compose/docker-compose.yml up -d

7. Once logged in, you can set up RDP and ssh. Use the default credentials `guacadmin / guacadmin`:

        http://<ip-or-host>:8080/guacamole/#/
        
    Note: use `Ctrl+Alt+Shift` to return to the menu.

8. Change the password of the admin user

9. Set up nginx (see `guacamole_site_nginx.conf`), replacing `guacamole.local` with the guacamole IP address or hostname from the perspective of the nginx server, and `guacamole.domain.com` with the domain name used. Make sure to generate certs with e.g. certbot.
