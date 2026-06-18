# -----------------------
# Firewall Rules
# -----------------------

resource "google_compute_firewall" "iap_ssh" {
  name    = "${var.resource_prefix}allow-iap-ssh"
  network = google_compute_network.topology_vpc.name

  direction     = "INGRESS"
  source_ranges = ["35.235.240.0/20"] # IAP proxy range

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  description = "Allow SSH via IAP tunnel"
}

resource "google_compute_firewall" "allow_ssh_again" {
  name    = "${var.resource_prefix}allow-ssh-again"
  network = google_compute_network.topology_vpc.name

  direction     = "INGRESS"
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  description = "Allow SSH access"
}
