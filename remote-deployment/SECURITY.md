# Security model for the remote-deployment examples

These examples (`topology-single-host`, `topology-partition`) provision **internet-exposed demo
servers** in GCP — meant for conferences, evaluations, and short-lived demos. They are deliberately
optimized for "anyone with a key can get in and drive the topology", **not** for production hardening.

This document collects the security constraints that apply to **both** topologies so they live in one
place. The per-topology READMEs link here. Each item below states the demo default, why it is the way
it is, and what to change for any non-demo use.

> **Bottom line:** treat these VMs as disposable and untrusted. Run them in an **isolated, disposable
> GCP project**, use **revocable, least-privilege credentials**, and tear them down when the demo is
> over. The mitigations below limit the blast radius; they do not make a demo VM production-safe.

## 1. SSH access — open by default, key-only

**Default:** SSH (port 22) is open to `0.0.0.0/0` via the `ssh_source_cidrs` Terraform variable, so
anyone with a valid key can connect from any network (e.g. conference WiFi). Password authentication
is **disabled** on the VM (Ansible writes `PasswordAuthentication no` to `sshd_config.d`), so only
holders of an authorized SSH key can log in.

**Why:** demo users connect from unpredictable networks; pre-restricting source IPs would lock them
out. Key-only auth removes the brute-force risk that makes open SSH "critical".

**Residual risk:** open SSH still exposes the VM to pre-auth SSH vulnerabilities and config drift.

**For non-demo use:** restrict SSH to trusted IPs by setting `ssh_source_cidrs`, e.g.

```hcl
ssh_source_cidrs = ["203.0.113.4/32"]  # your office / VPN egress IP(s)
```

Admin access via `gcloud compute ssh` (Google IAP, `35.235.240.0/20`) works regardless of this
setting. Proper production hardening (bastion/VPN, audit logging, intrusion detection) is out of scope.

**Reaching roaming users without opening port 22 — overlay/mesh VPN (recommended).** The reason the
default is `0.0.0.0/0` is that demo users connect from unpredictable IPs, so you can't pre-list them.
A mesh VPN solves this cleanly: every user and the VM get a stable private address on a private
network, and you keep port 22 closed to the public internet.

- **[Tailscale](https://tailscale.com)** is the lightest option. Install it on the VM
  (`curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`) and on each user's
  laptop, then set `ssh_source_cidrs = ["100.64.0.0/10"]` (the Tailscale CGNAT range) — or drop the
  public SSH rule entirely and connect over the tailnet IP / MagicDNS name. Access is gated by your
  Tailscale ACLs and is revocable per-device, so a conference attendee can be removed instantly
  without redeploying. Tailscale SSH can even replace key management. An ephemeral auth key can be
  baked into the VM provisioning if you want it joined automatically.
- **WireGuard** (already used by `topology-partition` for host-to-host) is the do-it-yourself
  equivalent: stand up a WireGuard interface and restrict SSH to the WireGuard subnet. More setup,
  no third-party dependency.
- **Google IAP TCP forwarding** works today with zero extra infra (`gcloud compute ssh` tunnels over
  `35.235.240.0/20`), but requires every user to have `gcloud` + project IAM access — usually too
  heavy for external demo users, fine for operators/admins.

## 2. RemotiveCloud token — readable on the VM, use a service account

**Default:** `topology-up` writes your cloud access token + organization to `/etc/environment` on the
VM so that interactive shells, non-interactive `ssh host "<cmd>"` (e.g. an app), and `docker compose`
all pick them up. Your local `~/.config/remotive` is **not** copied. `/etc/environment` is readable by
any user on the VM, and the `topology-user` account that runs the topology is in the `docker` group
(docker socket access is effectively root).

**Why / accepted limitation:** because the demo allows interactive TTY SSH and `remotive`/`docker`
need the token in the environment, the token **cannot be properly secured** against anyone who has a
shell on the box — they can read it from their own environment, `/proc`, or via docker regardless of
file permissions. Restricting file permissions would only break the workflow without closing the hole.

**Mitigation — limit the damage, don't try to hide it:** deploy with a dedicated, **revocable
RemotiveCloud service-account token** scoped to least privilege — never your personal credentials —
and revoke it once the demo is over.

`topology-single-host` **requires** this: `account_email` in your server's inventory file
(`servers/<server>.yaml`) is mandatory, so a deploy always uses a service-account token, not your
personal credentials. Create one and register it locally (see the README
[Create a service account](./topology-single-host/README.md#create-a-service-account)), then set
`account_email: <its email>` under `vars:`. `topology-up` authenticates with `--account <email>`, so
it deploys with the service-account token + org while your personal account stays active locally.
Each server's inventory file can use a different account.

## 3. GCP VM service account — broad by default, contain the blast radius

**Default:** the VM is deployed with the project's **default Compute Engine service account** and the
broad `cloud-platform` OAuth scope (`terraform/main.tf`). Its GCP access is therefore whatever IAM
roles that default account holds — often `roles/editor`, i.e. read/write to **all** project resources
(GCS buckets, other VMs, BigQuery, …).

**Risk:** since the VM is internet-exposed and not hardened, a compromise could reach your whole GCP
project, not just the demo. Unlike items 1 and 2, this risk leaks *outside* the disposable VM into
your real cloud account.

**The VM needs no GCP access** — images come from public registries and RemotiveCloud uses its own
token. For anything beyond a throwaway demo, especially in a **shared project**, attach a dedicated
service account with **no IAM roles**:

```hcl
resource "google_service_account" "vm" {
  account_id   = "${var.resource_prefix}vm"
  display_name = "Topology demo VM (no GCP access)"
}
# then in the instance's service_account block:
#   email  = google_service_account.vm.email
#   scopes = ["https://www.googleapis.com/auth/cloud-platform"]
```

With no roles bound, every GCP API call is denied regardless of scope. Check what the default account
holds today:

```sh
PROJ=<your-project>; NUM=$(gcloud projects describe "$PROJ" --format='value(projectNumber)')
gcloud projects get-iam-policy "$PROJ" \
  --flatten="bindings[].members" \
  --filter="bindings.members:${NUM}-compute@developer.gserviceaccount.com" \
  --format="table(bindings.role)"
```

**If the VM does need GCP access, grant narrow roles — never `roles/editor`/`roles/owner`.** Bind only
what a given capability requires to the dedicated SA above:

| Capability the VM needs | Minimal role | Notes |
| --- | --- | --- |
| Pull images from a **private** Artifact Registry | `roles/artifactregistry.reader` | Not needed for the public registries the examples use today. |
| Pull from legacy Container Registry (GCR/GCS-backed) | `roles/storage.objectViewer` | Scope it to the specific bucket if possible. |
| Ship logs to Cloud Logging | `roles/logging.logWriter` | Write-only; cannot read existing logs. |
| Ship metrics to Cloud Monitoring | `roles/monitoring.metricWriter` | Write-only. |
| Read one specific GCS bucket | `roles/storage.objectViewer` on that **bucket**, not the project | Use a bucket-level binding, not a project-level one. |

Example (Artifact Registry read only):

```hcl
resource "google_project_iam_member" "vm_artifactregistry" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.vm.email}"
}
```

Prefer **resource-level** bindings (on the bucket/repo) over project-level ones, and add roles one at
a time as a real need appears — not preemptively.

## 4. Topology-partition: WireGuard

`topology-partition` additionally opens **UDP/51820** to `0.0.0.0/0` for the WireGuard tunnel between
the two hosts. WireGuard is authenticated by key and silent to unauthenticated traffic, so this is
expected; it is not SSH and is not covered by `ssh_source_cidrs`.
