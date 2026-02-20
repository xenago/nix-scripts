# guacamole

Apache Guacamole web-based remote access portal.

## Deployment with Docker

1. Edit the compose file: 

  * Add temporary environment variables to the database container to initialize the instance with users, passwords, and a database:

        environment:
          - MARIADB_ROOT_PASSWORD=replace-with-db-root-password-here
          - MARIADB_PASSWORD=replace-with-db-service-account-password-here
          - MARIADB_USER=guacamole_user
          - MARIADB_DATABASE=guacamole_db

2. Generate the db initialization script:

       docker run --rm guacamole/guacamole /opt/guacamole/bin/initdb.sh --mysql > initdb.sql

3. Start mariadb:

       docker compose up -d guac-db

4. Watch the logs:

       docker logs guac-db

5. Once it has started, remove the environment variable section from the config and start it again:

       docker compose up -d guac-db

6. Run the initialization script for the new database in a container shell by piping it from the `guacamole` container:

       docker run --rm guacamole/guacamole:<CONTAINER-TAG-VERSION-HERE> /opt/guacamole/bin/initdb.sh --mysql | docker exec -it guac-db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" guacamole_db'

10. Start the other containers up:

        docker compose up -d

11. Once logged in, you can set up RDP and ssh. Use the default credentials `guacadmin / guacadmin`:

        http:/<ip-or-host>:8080/guacamole/#/
        
    Note: use Ctrl+Alt+Shift to return to the menu.

12. Change the password of the admin user

13. Set up nginx (see `guacamole_site_nginx.conf`), replacing `guacamole.local` with the guacamole IP address or hostname from the perspective of the nginx server, and `guacamole.domain.com` with the domain name used. Make sure to generate certs with e.g. certbot.
