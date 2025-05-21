# containers

Docker, podman, containerd, etc.

## Docker-related commands

Useful with docker and other associated tooling.

### Take down a single container started by compose

The equivalent of `docker compose down` but for a single container, useful if e.g. a hash is prepended to the name for some reason and you want to clean it up by recreating the container:

    docker-compose rm -s -v my-container

### Get a shell into an image with entrypoint/cmd

Sometimes images are stubborn and annoying to just get a simple shell running, but this usually works:

    docker run --rm -it --entrypoint /bin/sh cloverdx/cloverdx-server:6.7.1 -c sh

## Docker Compose notes

Useful when managing containers with Docker Compose.

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

## Troubleshooting

### Force docker service to start after mount is available

1. Check for mounts:

       systemctl list-unit-files | grep "\.mount "

Override the service - run `sudo systemctl edit docker.service` and add:

    [Unit]
    Requires=YOUR_MOUNT.mount
    After=YOUR_MOUNT.mount

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
