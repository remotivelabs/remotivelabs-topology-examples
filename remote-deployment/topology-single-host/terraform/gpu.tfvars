# Optional GPU. Pass this as the LAST -var-file so its machine_type/zone win:
#   terraform apply -var-file=<server>/server.auto.tfvars -var-file=gpu.tfvars
#
# Attachable GPUs require an N1 machine type. N1 also supports nested
# virtualization, so Cuttlefish/KVM keeps working alongside the GPU.
#
# The base region is already europe-west4 (it offers GPUs); this just pins the zone to
# europe-west4-c, where the nvidia-tesla-t4 is available (it's out of stock in -a).
zone         = "europe-west4-c"
machine_type = "n1-standard-16"
gpu_type     = "nvidia-tesla-t4"
gpu_count    = 1
