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

variable "resource_prefix" {
  type = string
}
