## Fixed EdgeShark Docker Compose File for Podman

This folder contains a docker compose file for running Edgeshark that has been fixed for Podman. You can start it as any other compose file:

```sh
podman compose -f docker-compose-localhost-podman.yaml up
```

For information about using Edgeshark, please see [the Edgeshark documentation](https://edgeshark.siemens.io/#/).

### Changes to the Original

You can find [the original file](https://github.com/siemens/edgeshark/raw/main/deployments/wget/docker-compose-localhost.yaml) in the Edgeshark repository of Siemens.

The only difference is that the `gostwire` service has an explicit hostname:

```
        hostname: 'gostwire.ghost-in-da-edge'
```

Docker automatically generates this from the service name and the network name, but podman doesn't.
