# Remote deployment

Examples for provisioning **internet-exposed demo servers** in GCP and deploying a complete Remotive
topology onto them — for conferences, evaluations, and short-lived demos. They are optimized for
"anyone with a key can get in and drive the topology", **not** for production hardening.

Two variants, depending on how the topology is spread across machines:

| Example                                            | What it does                                                                                             |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| [`topology-single-host`](./topology-single-host)   | Runs a complete topology on **one** GCP VM. Docker handles all internal networking. The simple case.     |
| [`topology-partition`](./topology-partition)       | **Splits** a topology across two machines (one in GCP, one local) over a WireGuard tunnel + VXLAN overlay. |

Each variant provisions its infrastructure with **Terraform** and configures/deploys with **Ansible**.
`topology-single-host` reuses the generic Ansible roles (`docker`, `remotivebus`, `remotive_cli`) from
`topology-partition/ansible/roles`, so that directory must stay in place.

Start with the per-example README for setup and run instructions.

## Security

These VMs are disposable and untrusted by design (open SSH, cloud token on the VM, broad GCP scope).
The security model shared by both examples — and what to change for any non-demo use — is in
[`SECURITY.md`](./SECURITY.md). **Read it before any non-demo use.**
