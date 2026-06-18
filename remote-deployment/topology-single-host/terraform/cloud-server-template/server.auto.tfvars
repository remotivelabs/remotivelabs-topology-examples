# A sample cloud server, sized for the remotive_car (Cuttlefish) topology. This is a
# TEMPLATE — copy the whole directory to create an isolated server (e.g. per customer
# or host):
#   cp -r cloud-server-template <server>
# then edit the values below and vm.backend.hcl.

# --- Identity (isolates this server) ---
# resource_prefix names every resource (VM, network, firewall, IP). Keep the trailing
# dash; different prefixes never clash. project_id is a placeholder — fill it in.
resource_prefix = "cloud-server-"
project_id      = "your-gcp-project-id"
region          = "europe-west4"
zone            = "europe-west4-a"

# --- VM (sized for the remotive_car Cuttlefish topology: x86 + nested virtualization) ---
machine_type                 = "c4-standard-8"
image_family                 = "ubuntu-2204-lts"
image_project                = "ubuntu-os-cloud"
enable_nested_virtualization = true
