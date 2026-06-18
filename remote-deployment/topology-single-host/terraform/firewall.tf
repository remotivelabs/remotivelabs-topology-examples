# -----------------------
# Firewall Rules
# -----------------------

# Admin access via `gcloud compute ssh` over the IAP tunnel — always available
# regardless of how ssh_source_cidrs is set.
resource "google_compute_firewall" "iap_ssh" {
  name    = "${var.resource_prefix}allow-iap-ssh"
  network = google_compute_network.topology_vpc.name

  direction     = "INGRESS"
  source_ranges = ["35.235.240.0/20"] # IAP proxy range

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  description = "Allow SSH via IAP tunnel (gcloud compute ssh)"
}

# Direct `ssh` access. Defaults to open (0.0.0.0/0) for demo convenience so
# anyone with a valid key can connect from any network (e.g. conference WiFi).
# Password auth is disabled on the VM, so key-only login is enforced. For any
# non-demo use, lock this down by setting ssh_source_cidrs to trusted IPs — see
# the README "SSH access" section.
resource "google_compute_firewall" "allow_ssh" {
  name    = "${var.resource_prefix}allow-ssh"
  network = google_compute_network.topology_vpc.name

  direction     = "INGRESS"
  source_ranges = var.ssh_source_cidrs

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  description = "Allow direct SSH from ssh_source_cidrs (default: anywhere, demo only)"
}
