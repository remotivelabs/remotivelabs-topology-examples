variable "project_id" {
  description = "Your GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region (default europe-west4 — also offers GPUs, so no region change needed for gpu.tfvars)"
  type        = string
  default     = "europe-west4"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "europe-west4-a"
}

variable "machine_type" {
  description = "Machine type"
  type        = string
  default     = "c4-standard-8"
}

variable "image_family" {
  type    = string
  default = "ubuntu-2204-lts"
}

variable "image_project" {
  type    = string
  default = "ubuntu-os-cloud"
}

variable "nodes_ip_cidr_range" {
  type    = string
  default = "10.3.0.0/24"
}

variable "node_ip" {
  type    = string
  default = "10.3.0.2"
}

variable "enable_nested_virtualization" {
  description = "Enable nested virtualization (x86 only; omit on ARM bare-metal where KVM is native)"
  type        = bool
  default     = true
}

variable "gpu_type" {
  description = "Attachable GPU type, e.g. nvidia-tesla-t4. Requires an N1 machine_type. Empty = no GPU."
  type        = string
  default     = ""
}

variable "gpu_count" {
  description = "Number of GPUs to attach (0 = none)"
  type        = number
  default     = 0
}

variable "resource_prefix" {
  description = "Unique per-server prefix that isolates this server (e.g. a customer/host name), trailing dash included. Set in <server>/server.auto.tfvars."
  type        = string
}

variable "ssh_source_cidrs" {
  description = "CIDRs allowed direct SSH (port 22). Defaults to anywhere for demo convenience (key-only auth is enforced on the VM). For non-demo use, restrict to trusted IPs, e.g. [\"203.0.113.4/32\"]. Admin access via `gcloud compute ssh` (IAP) works regardless of this setting."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
