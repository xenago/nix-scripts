# guacamole

Apache Guacamole web-based remote access portal.

## Deployment with Docker

Note: only works on x86 for now.

1. Edit the compose file: 

  * Replace `192.168.1.19` with the host IP address (it may be possible to use other networking modes to avoid this, but I generally find it easiest to do this if the host has a static private ipv4 address)
  * Add the temporary environment variable to set the root database password:

        environment:
          - MYSQL_ROOT_PASSWORD=set-your-random-root-password-here

2. Generate the db initialization script:

       docker run --rm guacamole/guacamole /opt/guacamole/bin/initdb.sh --mysql > initdb.sql

3. Start mariadb:

       docker compose up -d guac-db

4. Watch the logs:

       docker logs guac-db

5. Once it has started, remove the environment variable section from the config and start it again:

       docker compose up -d guac-db

6. Copy the initialization script into the container:

       docker cp initdb.sql mariadb:/guac_db.sql

7. Open a shell in the container:

       docker exec -it guac-db bash

8. Create a new database and user as shown below with your preferred password, using the mysql (mariadb) console. Log in using the mariadb root password, previously set:

       mysql -u root -p
       CREATE DATABASE guacamole_db;
       CREATE USER 'guacamole_user'@'%' IDENTIFIED BY 'guacamole_user_password';
       GRANT SELECT,INSERT,UPDATE,DELETE ON guacamole_db.* TO 'guacamole_user'@'%';
       FLUSH PRIVILEGES;
       quit

   While in the bash shell, create tables from the initialization script for the new database:

       cat guac_db.sql | mysql -u root -p guacamole_db
       mysql -u root -p
       use guacamole_db;
       show tables;
       exit  // should quit the mysql shell
       exit  // should quit the container

9. Edit the compose file and update the IP/hostnames as preferred. Make sure to set the new mariadb guacamole password.

10. Start the other containers up:

        docker compose up -d

11. Once logged in, you can set up RDP and ssh. Use the default credentials:

        http:/<ip>:8084/guacamole/#/
        guacadmin/guacadmin

    Note: use Ctrl+Alt+Shift to return to the menu.

12. Change the password of the admin user

13. Set up nginx (see `guacamole_site_nginx.conf`), replacing `192.168.1.19` with the guacamole container IP address (from the perspective of the nginx server). Make sure to generate certs with e.g. certbot.

