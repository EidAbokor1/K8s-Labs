# EKS Kubernetes Lab

## Overview

Production-grade EKS cluster deployed with Terraform, featuring automated TLS, DNS management, and GitOps with ArgoCD.

## Tools Used

- **Terraform** — Infrastructure as Code (EKS, VPC, IAM)
- **Helm** — K8s package manager
- **NGINX Ingress Controller** — Ingress/traffic management
- **Let's Encrypt** — Certificate authority
- **cert-manager** — Automates TLS certificate provisioning
- **external-dns** — Syncs ingress hosts with Route 53 DNS
- **ArgoCD** — GitOps continuous deployment

## Architecture

```
Internet → Route 53 (external-dns) → NLB → NGINX Ingress → Services → Pods
                                              ↑
                                     TLS (cert-manager + Let's Encrypt)
```

## Infrastructure

| Component | Details |
|-----------|---------|
| Cluster | EKS v1.31 |
| Region | eu-west-2 |
| VPC | 10.0.0.0/16 (3 AZs) |
| Worker Nodes | Managed node group (t3a.large / t3.large) |
| IRSA | cert-manager + external-dns |
| State | S3 backend |

## Deployed Apps

- **ArgoCD** — `argocd.eiddev.xyz`
- **app-hub** — `app-hub.eiddev.xyz`

## Usage

```bash
terraform init
terraform apply
kubectl apply -f cert-man/issuer.yml
kubectl apply -f argocd/app-argo.yml
```

## Cleanup

```bash
./scripts/cleanup.sh
```
