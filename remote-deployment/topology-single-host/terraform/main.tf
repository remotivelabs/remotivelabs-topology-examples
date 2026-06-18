terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  backend "gcs" {}
  required_version = ">= 1.6.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_network" "topology_vpc" {
  name                    = "${var.resource_prefix}topology-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "custom_subnet" {
  name          = "${var.resource_prefix}topology-subnet"
  ip_cidr_range = var.nodes_ip_cidr_range
  region        = var.region
  network       = google_compute_network.topology_vpc.id

  # Enable private access to Google APIs (so VMs can reach APIs without public IP)
  private_ip_google_access = true
}

resource "google_compute_instance" "topology_vm" {
  allow_stopping_for_update = true

  name         = "${var.resource_prefix}node1"
  machine_type = var.machine_type
  zone         = var.zone
  tags         = ["vm1"]

  scheduling {
    on_host_maintenance = "TERMINATE"
  }

  dynamic "advanced_machine_features" {
    for_each = var.enable_nested_virtualization ? [1] : []
    content {
      enable_nested_virtualization = true
    }
  }

  # Optional NVIDIA GPU (attachable on N1 machine types). Empty/0 = no GPU.
  dynamic "guest_accelerator" {
    for_each = var.gpu_count > 0 ? [1] : []
    content {
      type  = var.gpu_type
      count = var.gpu_count
    }
  }

  boot_disk {
    initialize_params {
      image = "${var.image_project}/${var.image_family}"
      size  = 100
    }
  }

  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  network_interface {
    network    = google_compute_network.topology_vpc.id
    subnetwork = google_compute_subnetwork.custom_subnet.id
    # Assign a deterministic internal IP
    network_ip = var.node_ip

    access_config {
      nat_ip = google_compute_address.vm_ip.address
    }
  }
}

# Reserved static external IP, part of this server. Stable while the server exists
# (survives VM stop/restart); released on `terraform destroy`.
resource "google_compute_address" "vm_ip" {
  name   = "${var.resource_prefix}node1"
  region = var.region
}

output "vm_name" {
  value = google_compute_instance.topology_vm.name
}

output "node_1" {
  value = "${google_compute_instance.topology_vm.name} = ${google_compute_instance.topology_vm.network_interface[0].access_config[0].nat_ip}"
}

output "node_ip" {
  value = google_compute_instance.topology_vm.network_interface[0].access_config[0].nat_ip
}

# Ready-to-run SSH command with project + zone baked in (no gcloud defaults needed).
# Run it directly: $(terraform output -raw ssh_command)
output "ssh_command" {
  value = "gcloud compute ssh ubuntu@${google_compute_instance.topology_vm.name} --project ${var.project_id} --zone ${var.zone}"
}
