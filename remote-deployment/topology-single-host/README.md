# Single-host topology

This sample provisions **one** GCP machine and runs a complete Remotive topology on it. It can deploy
**any** topology — you pick which one with a named **profile** (`-e topology=<name>`).

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

Each topology is described by two small files:

- `ansible/topologies/<name>.yaml` — project dir, instance `-f` files, compose overlays/profiles, ports
- `terraform/topologies/<name>.tfvars` — the VM (machine type / image / nested virtualization)

Shipped profiles:

| Profile        | Project (relative to `examples/`) | VM                                          |
| -------------- | --------------------------------- | ------------------------------------------- |
| `remotive_car` | `remotive_car`                    | x86 `c4-standard-8`, nested virtualization  |

> Profile `topology_dir` values are relative to the `examples/` directory (where `remote-deployment`
> and `remotive_car` are siblings).

## Prerequisites

On the host where you run Terraform/Ansible you need: Terraform, Ansible, the `gcloud` cli, and the
`remotive` cli (>= 0.5.0a1). Cuttlefish-based topologies ship their own map APK; see the topology's
own README for any per-topology prerequisites.

**Authenticate first.** `topology-up` reads your active account + default org locally (it cannot
drive the interactive pickers), so set them up once in your terminal beforehand:

```sh
remotive cloud auth activate          # or: remotive cloud auth login
remotive cloud organizations default  # select your organization
```

In the steps below, set the profile once:

```sh
export TOPOLOGY=remotive_car
```

## Setup Terraform

Initialize a personal terraform stack so you don't clash with other users. Resources are prefixed
with your username.

```sh
cd terraform
cp dev/example.auto.tfvars dev/$(whoami).auto.tfvars
cp dev/example.backend.hcl dev/$(whoami).backend.hcl
sed -i "s/example/$(whoami)/g" dev/$(whoami).auto.tfvars dev/$(whoami).backend.hcl
# On mac
# sed -i "" "s/example/$(whoami)/g" dev/$(whoami).auto.tfvars dev/$(whoami).backend.hcl

terraform init -backend-config=dev/$(whoami).backend.hcl -reconfigure --upgrade
```

## Deploy terraform

Pass the topology's tfvars so the right VM (architecture/size) is provisioned:

```sh
cd terraform
terraform apply -var-file=dev/$(whoami).auto.tfvars -var-file=topologies/$TOPOLOGY.tfvars
```

This deploys a single VM in GCP. Take note of its public IP. You can SSH to the machine using the
command below. It may take 1-2 minutes after Terraform finishes before SSH works.

```sh
gcloud compute ssh ubuntu@$(whoami)-remotive-node1
```

If you have not done this before this creates an SSH key in `~/.ssh/` that is used with Google VMs.
Ansible is configured to use this key and expects it.

## Setup Ansible

Copy `inventory.ini.template` to `inventory.ini` and set the public IP of the VM. The host must stay
in the `remote` group.

## Prepare the node

Install all dependencies (Docker, CAN utilities, remotivebus, remotive CLI) on the VM:

```sh
cd ansible
ansible-playbook -K -e topology=$TOPOLOGY playbooks/dependencies.yaml
```

## Run topology

```sh
ansible-playbook -K -e topology=$TOPOLOGY playbooks/topology-up.yaml
```

Stop the topology with:

```sh
ansible-playbook -K -e topology=$TOPOLOGY playbooks/topology-down.yaml
```

## Observing the topology

When the topology is running, SSH to the VM and forward the ports listed in the profile's
`forward_ports` (for `remotive_car`: 8080, 8443, 50051, 3000):

```sh
gcloud compute ssh ubuntu@$(whoami)-remotive-node1 -- -q -L 8080:localhost:8080 -L 8443:localhost:8443 -L 50051:localhost:50051 -L 3000:localhost:3000
```

Then visit the topology's URLs (e.g. <http://localhost:8080> for the web app, <https://localhost:8443>
for Cuttlefish).

## Adding a new topology

1. Drop `ansible/topologies/<name>.yaml` (copy an existing one; set `topology_dir`,
   `topology_instances`, `compose_overlays`, `compose_profiles`, `forward_ports`).
2. Drop `terraform/topologies/<name>.tfvars` with the VM that topology needs.
3. Deploy with `-e topology=<name>` / `-var-file=topologies/<name>.tfvars`.

## Cleaning up

Once you are done, tear down the environment to avoid having the cloud instance running and costing
money:

```sh
cd terraform
terraform destroy -var-file=dev/$(whoami).auto.tfvars -var-file=topologies/$TOPOLOGY.tfvars
```
