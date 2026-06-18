# Topology partition

This sample shows how to partition a topology across two Linux machines, one in GCP and one running locally.

## Prerequisites

You will need a local Linux with Ubuntu/Debian. This can either be your host system or a VM which you can SSH into.

When using a VM you can still run the Terraform and Ansible commands from your host system, if that is where you have this repository. The VM is then only used for running the topology. You can of course run everything from within a VM if that is where you have this repository.

### Installed software

On the host where this is running you need the following applications installed.

- Terraform
- Ansible
- Wireguard (wireguard-tools on mac)
- `gcloud` cli
- `remotive` cli (version >= 0.5.0a1)

You should also have a [maps APK](https://f-droid.org/repo/app.organicmaps_25121616.apk) downloaded and placed into the `remotive_car/instances/android/cuttlefish/apks/` folder.

### Authenticate

`topology-up` reads your active account + default organization locally (it cannot drive the
interactive pickers) and sets them as env vars on the hosts — your `~/.config/remotive` is not
copied. Set them up once beforehand:

```sh
remotive cloud auth activate          # or: remotive cloud auth login
remotive cloud organizations default  # select your organization
```

## Setup Terraform

Start by initializing a personal terraform stack. This will prevent clashing with other users. Resources will be prefixed with your username. If other prefix is desired, edit files manually.

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

```sh
cd terraform
terraform apply -var-file=dev/$(whoami).auto.tfvars
```

This will deploy a VM in GCP. Take note of the IP of the machine. You can SSH to the machine using
It may take a little while after the terrafom job is done until you can ssh into it due to provisioning done
after the instance is created, 1-2 minutes is expected

```sh
gcloud compute ssh ubuntu@$(whoami)-remotive-node1
```

If you have not done this before this will create an SSH key in `~/.ssh/` that is used with Google VMs. Ansible is configured to use this key and expects it.

## Setup Ansible

To prepare Ansible you need to create an `inventory.ini` file which contains the hosts and how to connect to them. Copy `inventory.ini.template` and update the IP addresses, user names and SSH key paths.

## Prepare nodes

To prepare the machines we want to ensure it has all dependencies installed and setup a secure Wireguard tunnel between them. This is done using two Ansible scripts. Run them with

```sh
cd ansible
ansible-playbook -K playbooks/dependencies.yaml # you can add '--limit remote' if you do not wish to install things on your local VM
ansible-playbook -K playbooks/wireguard.yaml
```

## Run topology

The following playbook will setup the networks on the machines, generate the topologies, copy the files over and start the containers.

```sh
ansible-playbook -K playbooks/topology-up.yaml
```

You can stop the topology (and clean up the networks) with

```sh
ansible-playbook -K playbooks/topology-down.yaml
```

## Observing the topology

When the topology is running you should be able to observe it if you SSH to either of the machines and forward the web, broker, Cuttlefish ports. E.g. for the cloud instance which runs Cuttlefish:

```sh
gcloud compute ssh ubuntu@$(whoami)-remotive-node1 -- -q -L 8443:localhost:8443 -L 8080:localhost:8080 -L 50051:localhost:50051 -L 5001:localhost:5001
```

Then visit the <https://localhost:8443> or <http://localhost:8080> as normal.

## Cleaning up

Once you are done you should tear down the environment to avoid having the cloud instance running and costing money. Do this by running

```sh
cd terraform
terraform destroy -var-file=dev/$(whoami).auto.tfvars
```
