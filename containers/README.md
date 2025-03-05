# containers

Docker, podman, containerd, etc.

## Useful docker-related commands

1. The equivalent of `docker compose down` but for a single container, useful if e.g. a hash is prepended to the name for some reason and you want to clean it up by recreating the container:

       docker-compose rm -s -v yourService

2. Get a shell into a stubborn image with entrypoint/cmd:

       docker run --rm -it --entrypoint /bin/sh cloverdx/cloverdx-server:6.7.1 -c sh

4. Keep a `compose` container running using a no-op process:

       services:
         my-container:
           image: cloverdx/cloverdx-server:6.7.1
           restart: always
           entrypoint: /bin/sh
           command: -c 'tail -f /dev/null'
