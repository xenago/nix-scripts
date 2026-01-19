# containers

Docker, podman, containerd, etc.

## Docker-related commands

Useful with docker and other associated tooling.

### Take down a single container started by compose

The equivalent of `docker compose down` but for a single container, useful if e.g. a hash is prepended to the name for some reason and you want to clean it up by recreating the container:

    docker-compose rm -s -v my-container

### Open an interactive shell in a running container

    docker exec -it container-name sh

### Start a container with an interactive shell

Most of the time, this should work:

    docker run --rm --it container/image:latest sh

Note: the `--rm` flag will clean up and delete the container when it exists; omit that to keep it listed in e.g. `docker ps -a`.

### Bypass entrypoint/cmd when running

Sometimes images are stubborn and annoying to just get a simple interactive root shell running, but this usually works:

    docker run --rm -it -u root --entrypoint /bin/sh container/image:latest -c sh

## Docker Compose notes

Useful when managing containers with Docker Compose.

### Enumerate containers and stacks running on the machine

For a basic output:

    docker compose ls

It will look something like:

    user@machine:~$ docker compose ls
    NAME                STATUS              CONFIG FILES
    code-server-stack   running(1)          /home/user/containers/code-server/compose/docker-compose.yml
    filebrowser-stack   running(1)          /home/user/containers/filebrowser/compose/docker-compose.yml
    gitlab-stack        running(2)          /home/user/containers/gitlab/compose/docker-compose.yml

To filter and manipulate, output in JSON and pipe into tools like `jq`:

    docker compose ls --format json | jq -r 'if type=="array" then .[] else . end | .Name' | while read -r project; do     docker compose -p "$project" ps --all --format "{{.Project}}\t{{.Name}}\t{{.Image}}\t{{.Status}}"; done | column -t -s $'\t' -N STACK,CONTAINER,IMAGE,STATUS

The more detailed output will look something like:

    STACK              CONTAINER                    IMAGE                                STATUS
    code-server-stack  code-server                  codercom/code-server:4.108.1-debian  Up About an hour
    filebrowser-stack  filebrowser                  filebrowser/filebrowser:v2.50.0-s6   Up 45 minutes (healthy)
    gitlab-stack       gitlab                       gitlab/gitlab-ce:18.7.1-ce.0         Up 44 minutes (healthy)
    gitlab-stack       gitlab-runner                gitlab/gitlab-runner:v18.7.2         Up 44 minutes

### Keep a container running using a no-op process

Sometimes a container will quit immediately upon starting, which is not helpful if you want to actively have the environment 'up' for some reason. This allows for a container to be brought up as a kind of blank zombie without the usual PID 1 starting.

       services:
         my-container:
           image: cloverdx/cloverdx-server:6.7.1
           restart: always
           entrypoint: /bin/sh
           command: -c 'tail -f /dev/null'

### Control startup order

It is possible to specifically control startup order of containers to prevent them from starting before another is healthy, for example.

https://docs.docker.com/compose/how-tos/startup-order/

https://stackoverflow.com/questions/31746182/docker-compose-wait-for-container-x-before-starting-y

In this example, the first container waits for another container named `my-one-shot-container` to finish successfully before it can start, and the second container waits for another container to be up and running before it can start:

    services:
      my-container:
        depends_on:
          my-one-shot-container:
            condition: service_completed_successfully
      another-container:
        depends_on:
          my-long-running-container:
            condition: service_healthy

### Reasonable health checks

Here is an example config with a working healthcheck for the official MariaDB container:

    mariadb:
      image: mariadb:10.11
      container_name: mariadb
      hostname: mariadb
      environment:
        - MARIADB_MYSQL_LOCALHOST_USER=1
      restart: unless-stopped
      volumes:
        # Store data in a sibling folder away from the compose file
        - ../data/mariadb/mysql:/var/lib/mysql
      ports:
        - 3306:3306
      healthcheck:
        test: ["CMD", "healthcheck.sh", "--su-mysql", "--connect", "--innodb_initialized"]
        start_period: 20s
        start_interval: 5s
        interval: 30s
        timeout: 5s
        retries: 3

Many container images have poorly-documented health checks or none built in at all, so the test command and setup will vary a lot.

## Troubleshooting

### Force docker service to start after mount is available

1. Check for mounts:

       systemctl list-unit-files | grep "\.mount "

Override the service - run `sudo systemctl edit docker.service` and add:

    [Unit]
    Requires=YOUR_MOUNT.mount
    After=YOUR_MOUNT.mount

Note: this will prevent docker from starting if the mountpoint fails. Be sure to take this into account when configuring the system!

### Resolve `Cannot connect to the Docker daemon at unix:///var/run/docker.sock` error

1. Ensure `/var/run/docker.sock` is not a directory (if so, delete it)
2. Override the service and add the socket manually:

   https://superuser.com/a/1852442

   Run `sudo systemctl edit docker.service` and add:
       
       [Service]
       ExecStart=
       ExecStart=/usr/bin/dockerd -H unix:///var/run/docker.sock -H fd:// --containerd=/run/containerd/containerd.sock

   Run `sudo systemctl daemon-reload` to pick up the changes.

3. Restart the service:

       sudo systemctl reset-failed docker
       sudo systemctl restart docker
