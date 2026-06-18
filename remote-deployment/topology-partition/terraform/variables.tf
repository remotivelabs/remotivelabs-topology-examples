variable "project_id" {
  description = "Your GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-north1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "europe-north1-a"
}

variable "machine_type" {
  description = "Machine type"
  type        = string
  default     = "c4-standard-8"
  # default     = "c4a-highmem-96-metal"
}

variable "image_family" {
  type    = string
  default = "ubuntu-2204-lts"
  # default = "ubuntu-2404-lts-arm64"
}

variable "image_project" {
  type    = string
  default = "ubuntu-os-cloud"
}

variable "nodes_ip_cidr_range" {
  type    = string
  default = "10.3.0.0/24"
}

variable "node_ips" {
  type    = list(any)
  default = ["10.3.0.2"]
}

variable "resource_prefix" {
  type = string
}

variable "ssh_source_cidrs" {
  description = "CIDRs allowed direct SSH (port 22). Defaults to anywhere for demo convenience (key-only auth is enforced on the VM). For non-demo use, restrict to trusted IPs, e.g. [\"203.0.113.4/32\"]. Admin access via `gcloud compute ssh` (IAP) works regardless of this setting."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
