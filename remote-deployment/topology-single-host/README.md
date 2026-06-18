# Single-host topology

This sample provisions a single GCP **server** (one VM with its own private network and reserved IP)
and deploys a complete Remotive topology onto it. It can run **any** topology — you pick which one per
deploy with `-e topology=<name>`.

Every deployment is its **own isolated server**: you name it (e.g. after a customer or host), and that
name prefixes a private VPC, subnet, firewall, VM, and a reserved external IP, all in its own
Terraform state. Different servers never clash and any one can be **destroyed on its own** without
touching the others — so multiple customers can run side by side on separate hosts. The **use-case**
(which topology runs, and the machine size/arch it needs) is a separate axis, selected per deploy.

It is the simple counterpart to [`../topology-partition`](../topology-partition), which splits a
topology across two machines using a WireGuard tunnel and a VXLAN overlay. Here there is no
cross-host networking at all — everything runs on a single VM and Docker handles the internal
networking.

The generic Ansible roles (`docker`, `remotivebus`, `remotive_cli`) are reused directly from
`../topology-partition/ansible/roles` via `roles_path` in `ansible/ansible.cfg`, so that directory
must stay in place.

## How it works

A topology is treated as a **self-contained project directory**. On `topology-up` the playbook:

1. reads your cloud access token + organization locally and writes them to `/etc/environment` on the
   VM (so every SSH session — terminal or app — picks them up); your `~/.config/remotive` is **not**
   copied to the VM,
2. rsyncs the whole topology project directory to the VM,
3. runs `remotive topology build` **on the VM** (so all baked paths resolve against the VM's home),
4. starts the generated `docker compose` together with the profile's overlays/profiles.

> **Security:** the cloud token written to `/etc/environment` is readable by anyone with a shell on
> the VM — use a revocable, least-privilege RemotiveCloud service-account token, not your personal
> credentials. This and the other demo security constraints (SSH exposure, GCP VM service-account
> scope) are documented in [`../SECURITY.md`](../SECURITY.md). **Read it before any non-demo use.**

The two axes are kept separate:

- **Use-case (topology)** — `ansible/topologies/<name>.yaml` (project dir, instance `-f` files,
  compose overlays/profiles, ports), selected with `-e topology=<name>`.
- **Server (deployment)** — a directory under `terraform/` named after the server (copy
  `cloud-server-template/`). Its `server.auto.tfvars` carries identity (`resource_prefix`, project,
  region) plus the VM spec (machine type / image / nested virtualization), and `vm.backend.hcl` gives
  it its own Terraform state.

Shipped profiles:

| Profile        | Project (relative to repo root)   | Server spec it needs              |
| -------------- | --------------------------------- | --------------------------------- |
| `remotive_car` | `remotive_car`                    | x86 `c4-standard-8`, nested virt  |

> Profile `topology_dir` values are relative to the repo root (where `remote-deployment`
> and `remotive_car` are siblings). The **Server spec** column is what the topology needs from the VM
> — you set it on the server in `server.auto.tfvars`, not in the profile (the `cloud-server-template`
> sample already matches `remotive_car`).

## Prerequisites

On the host where you run Terraform/Ansible you need: Terraform, Ansible, the `gcloud` cli, and the
`remotive` cli (version >= 0.23.0). Cuttlefish-based topologies ship their own map APK; see the
topology's own README for any per-topology prerequisites.

### Create a service account

This example deploys as a dedicated, **revocable RemotiveCloud service account** — never your
personal credentials (see [`../SECURITY.md`](../SECURITY.md)). This is required: `topology-up`
reads the account's token + default org locally (it cannot drive the interactive pickers) and
sets them on the VM.

First log in as yourself — you need this to create the service account:

```sh
remotive cloud auth login
```

Then create the service account, download a token for it, and register it locally:

```sh
# 1. Create the service account in your project
remotive cloud service-accounts create <name> --role org/topologyRunner --role org/studioRunner --project <project-id>

# 2. Create + download an access token for it
remotive cloud service-accounts tokens create --service-account <name> --project <project-id>

# 3. Register it locally AND set its default organization. The org MUST be set while the
#    service account is the active account — `--account` only prints, it cannot set the org.
remotive cloud auth activate <downloaded-token-file>
remotive cloud auth organization set --it

# 4. Note its email — this is the account_email you set per server
remotive cloud auth list
```

Set `account_email: <its email>` under `vars:` in your server's inventory file
(`servers/<server>.yaml`, see Setup Ansible below) — it is **required**. `topology-up`
authenticates with `--account <email>`, so you can switch your own account back to active at any
time (`remotive cloud auth activate <you>`) without affecting deploys. Each server's inventory can
target its own service account.

## Setup Terraform

`cloud-server-template/` is the sample server. Copy it to a directory named after your server (a
customer or host name) — everything unique to the server lives there and is gitignored, so servers
stay fully isolated:

```sh
cd terraform
cp -r cloud-server-template acme   # "acme" = your server name
# Edit acme/server.auto.tfvars -> resource_prefix = "acme-", project_id (+ region/zone, VM spec)
# Edit acme/vm.backend.hcl     -> bucket + a unique prefix (e.g. ...-acme)
export SERVER=acme
```

## Deploy terraform

The server directory's files supply identity, VM spec, and state — a single `-var-file`:

```sh
terraform init  -backend-config=$SERVER/vm.backend.hcl -reconfigure --upgrade
terraform apply -var-file=$SERVER/server.auto.tfvars
```

This deploys a single VM with a reserved static IP (printed as the `node_ip` output). SSH to it with
the ready-made `ssh_command` output — it bakes in the project and zone, so no gcloud defaults are
needed (it may take 1-2 minutes after Terraform finishes before SSH works):

```sh
$(terraform output -raw ssh_command)
```

On first use this creates `~/.ssh/google_compute_engine`, the key gcloud uses for Google VMs; Ansible
is configured to use that key and expects it.

> **SSH access — demo default is open (`0.0.0.0/0`), key-only.** Anyone with a valid key can connect
> from any network; password auth is disabled. For non-demo use, restrict it via `ssh_source_cidrs` in
> `server.auto.tfvars`. See [`../SECURITY.md`](../SECURITY.md) for the rationale and the secure setup.

Get the IP of the host:

```sh
terraform output -raw node_ip
```

## Setup Ansible

Pick the use-case (topology) for the Ansible steps below:

```sh
cd ansible
export TOPOLOGY=remotive_car
cp servers/cloud-server-template.yaml servers/$SERVER.yaml
```

Set the public IP of the VM under `remote: hosts:`. This `$SERVER.yaml` contains all settings for
the server including the required `account_email` service-account var (see "Create a service
account" above) and the `topology-user` SSH keys (see below). The host must stay in the `remote`
group. The IP is a reserved static address, so it is stable while the server exists (it only
changes if you destroy
and recreate the server). You select which server a run targets with `-i servers/$SERVER.yaml`.

## Prepare the server

Prepare the VM in one step — installs all dependencies (Docker, CAN utilities, remotivebus, remotive
CLI) **and** creates the `topology-user` account that runs the topology (see
[The `topology-user` account](#the-topology-user-account) below):

```sh
cd ansible
ansible-playbook -i servers/$SERVER.yaml playbooks/prepare-server.yaml
```

Set `topology_user_authorized_keys` in your server's inventory file first (see below) — the step
fails without at least one key. `prepare-server.yaml` just runs `dependencies.yaml` then
`topology-user.yaml`; both are idempotent and can be run on their own (e.g. re-run
`topology-user.yaml` any time to add or revoke a key).

## Run topology

```sh
ansible-playbook -i servers/$SERVER.yaml -e topology=$TOPOLOGY playbooks/topology-up.yaml
```

Stop the topology with (it tears down whatever is running on the host — no `-e topology` needed):

```sh
ansible-playbook -i servers/$SERVER.yaml playbooks/topology-down.yaml
```

## The `topology-user` account

`prepare-server` creates a dedicated `topology-user` that **owns and runs** the topology, so you can
hand out access (e.g. to a customer) without giving away the `ubuntu` admin account. Admins connect
as `ubuntu` (sudo, gcloud-managed key); everyone else connects as `topology-user`. The topology is
deployed into `~topology-user/projects/<topology>` and runs as that user.

It is created as part of `prepare-server.yaml` (which runs `dependencies.yaml` then
`topology-user.yaml`), so the normal order is **`prepare-server` → `topology-up`**. You can also run
`topology-user.yaml` on its own — e.g. to add or revoke a key after the server is up.

> The deploy user is `topology-user`; `topology-up` falls back to the `ubuntu` connection user only
> if `topology-user` was never created (`/home/ubuntu/projects/<topology>`). Force a specific one with
> `-e deploy_user=<name>`. **Switching is safe:** `topology-down` tears down whatever is running
> regardless of who started it (and `topology-up` runs it first), so switching the deploy user and
> re-running `topology-up` stops the old stack and redeploys under the new one.

Keys are **per server** — they live in that server's inventory file
`ansible/servers/<server>.yaml` (the same file you set the IP in), as the
`topology_user_authorized_keys` list.

1. Add the public keys that may log in under `vars:` in this server's inventory file (e.g.
   `ansible/servers/acme.yaml`). A key listed here is the **only** way in, and grants access
   **only** as `topology-user`:

   ```yaml
   remote:
     hosts:
       <vm-ip>:
     vars:
       topology_user_authorized_keys:
         - "ssh-ed25519 AAAA... alice@laptop"
   ```

2. Apply the list. `prepare-server.yaml` applies it initially; afterwards re-run `topology-user.yaml`
   any time you add or remove a key (the list is the source of truth, so removing one and re-running
   revokes it), selecting that server's inventory file with `-i`:

   ```sh
   cd ansible
   ansible-playbook -i servers/$SERVER.yaml playbooks/topology-user.yaml
   ```

Now `ssh topology-user@<host>` lands in a normal shell that can drive the topology (cloud auth is
already exported on the host by `topology-up`, so it can reach the broker/cloud):

```
$ ssh topology-user@host
$ cd ~/projects/<topology>     # the deployed workspace, owned by topology-user
$ remotive broker ...          # works
$ docker compose ps            # works (topology-user is in the docker group)
$ sudo ...                     # not available — no sudo
```

**Scope & limits:** the role only manages `topology-user`, its `~/projects` workspace, and its
authorized keys — it does not touch the `ubuntu` admin account or global SSH config. The account
has **no sudo** and a `0750` home, so it is isolated from other users' files. It **is** in the
`docker` group (required so `remotive` can drive Docker) — and docker-socket access is effectively
root on the box, so treat it as a trust boundary, not a sandbox.

## SSH config (optional)

To avoid retyping the IP, user, and key, add host aliases to `~/.ssh/config`. Both users share the
same VM (`terraform output -raw node_ip`); they differ only in `User` and `IdentityFile`:

```ssh-config
# Shared: same VM for both users. StrictHostKeyChecking/UserKnownHostsFile mirror
# ansible.cfg and prevent the "REMOTE HOST IDENTIFICATION HAS CHANGED" error when a
# destroy + re-apply gives the reserved IP a new host key. (This drops MITM protection
# — fine for an ephemeral demo server, not for long-lived hosts.)
Host myserver myserver-topology
    HostName <node_ip>
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR

# Admin — the gcloud-managed key (authorized on your first `gcloud compute ssh`).
Host myserver
    User ubuntu
    IdentityFile ~/.ssh/google_compute_engine

# topology-user — the key you listed in ansible/servers/<server>.yaml.
Host myserver-topology
    User topology-user
    IdentityFile ~/.ssh/id_ed25519
```

Then `ssh myserver` (admin) or `ssh myserver-topology` (the topology account). Forward the topology
UIs by appending `-L` to the alias:

```sh
ssh myserver-topology -L 8080:localhost:8080 -L 8443:localhost:8443 -L 50051:localhost:50051 -L 3000:localhost:3000
```

> If you'd rather keep strict host-key checking and you hit `REMOTE HOST IDENTIFICATION HAS CHANGED`
> after a destroy + re-apply (the reserved IP stays, the host key doesn't), just drop the stale entry
> with `ssh-keygen -R <node_ip>` and reconnect.

## Observing the topology

When the topology is running, SSH to the VM and forward the ports listed in the profile's
`forward_ports` (for `remotive_car`: 8080, 8443, 50051, 3000):

```sh
$(terraform output -raw ssh_command) -- -q -L 8080:localhost:8080 -L 8443:localhost:8443 -L 50051:localhost:50051 -L 3000:localhost:3000
```

Then visit the topology's URLs (e.g. <http://localhost:8080> for the web app, <https://localhost:8443>
for Cuttlefish).

## Optional: GPU

To attach an NVIDIA GPU to the VM, pass `gpu.tfvars` as the **last** `-var-file` (so its
`machine_type` and zone win):

```sh
terraform apply -var-file=$SERVER/server.auto.tfvars -var-file=gpu.tfvars
```

`gpu.tfvars` uses an **N1** machine (`n1-standard-16`) with an attachable `nvidia-tesla-t4` — N1
supports both attachable GPUs and the nested virtualization Cuttlefish needs. Edit it for a different
GPU/size. (T4 capacity varies by zone.)

The NVIDIA **driver + Container Toolkit + CDI spec** install automatically on the next
`dependencies.yaml` run — it detects the card via `lspci` and runs the `nvidia` role only when one is
present. The first such run **may reboot the VM once** to load the kernel module; the CDI spec
(`/etc/cdi/nvidia.yaml`, which Docker reads to resolve `gpus: all`) is generated once the driver is
live in that same run. To regenerate it after a driver/GPU change, delete the file and re-run.

Expose the GPU to a container in your topology, e.g. in a compose overlay or the container block:

```yaml
services:
  <service>:
    gpus: all          # or: deploy.resources.reservations.devices: [{ capabilities: [gpu] }]
```

### Cuttlefish GPU mode (auto-detected)

The GPU is **opt-in per host, automatically**. The base `cuttlefish.compose.yaml` overlay requests no
GPU, so the topology starts on any VM (Cuttlefish falls back to software rendering). The GPU-only bits
live in a separate `cuttlefish.gpu.compose.yaml` overlay (`gpus: all`,
`CUTTLEFISH_GPU_MODE=gfxstream_guest_angle`, and the `libvulkan1` install), declared in the topology's
`gpu_compose_overlays`. `topology-up.yaml` runs `lspci` on the host and layers that overlay in **only
when a card is present** — so the same topology runs GPU-accelerated on a GPU VM and software-rendered
everywhere else, with no config change.

Why the split: a `gpus: all` request on a host without a GPU fails the whole `docker compose up` with
`failed to discover GPU vendor from CDI: no known GPU vendor found`. Keeping it out of the base overlay
is what lets the stack start without a GPU.

`CUTTLEFISH_GPU_MODE` values (set in the GPU overlay):

- `gfxstream_guest_angle` / `gfxstream` — GPU-accelerated rendering via the host's Vulkan driver.
  Requires `gpus: all` **and** a Vulkan loader (`libvulkan1`) present in the Cuttlefish image — the GPU
  overlay installs it via an entrypoint wrapper before launching `cvd`.
- `guest_swiftshader` — software rendering; no GPU required.

If the variable is left unset, Cuttlefish defaults to `auto`, which on these VMs detects nothing usable
and selects SwiftShader — i.e. **no GPU acceleration**. The GPU overlay sets it explicitly to get
hardware rendering.

## Adding a new topology (use-case)

1. Drop `ansible/topologies/<name>.yaml` (copy an existing one; set `topology_dir`,
   `topology_instances`, `compose_overlays`, `compose_profiles`, `forward_ports`).
2. Make sure the server you deploy it on has a suitable VM spec in its `server.auto.tfvars` (the
   `cloud-server-template` sample is sized for the Cuttlefish topology; adjust `machine_type` etc. if
   the topology needs something different).
3. Deploy with `-e topology=<name>` on the Ansible side.

## Adding a new server (deployment)

`cp -r terraform/cloud-server-template terraform/<server>`, edit `resource_prefix`, `project_id` and
the backend prefix to unique values, then run **Setup/Deploy terraform** with `SERVER=<server>`. It is
fully isolated from every other server — its own network, VM, IP, and state.

## Cleaning up

Each server tears down on its own — destroying one never touches another. This removes everything in
the server, including its reserved IP (you won't get the same address back):

```sh
cd terraform
terraform destroy -var-file=$SERVER/server.auto.tfvars
```
