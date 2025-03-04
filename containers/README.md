# containers

Docker, podman, containerd, etc.

## Useful docker-related commands

1. The equivalent of `docker compose down` but for a single container, useful if e.g. a hash is prepended to the name for some reason and you want to clean it up by recreating the container:

       docker-compose rm -s -v yourService

2. Get a shell into a stubborn image:

       docker run --rm -it --entrypoint /bin/sh image-name -c sh
