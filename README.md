# EKS Status Hub

## Overview

Production-grade EKS cluster deployed with Terraform, featuring an EKS Status Hub app to track the health of Kubernetes components, automated TLS, DNS management, GitOps with ArgoCD, monitoring with Prometheus/Grafana, and CI/CD with GitHub Actions.

## Tools Used

- **Terraform** — Infrastructure as Code (EKS, VPC, IAM)
- **Helm** — K8s package manager
- **NGINX Ingress Controller** — Ingress/traffic management
- **Let's Encrypt** — Certificate authority
- **cert-manager** — Automates TLS certificate provisioning
- **external-dns** — Syncs ingress hosts with Route 53 DNS
- **ArgoCD** — GitOps continuous deployment
- **Prometheus** — Cluster metrics collection
- **Grafana** — Metrics visualisation and dashboards
- **GitHub Actions** — CI/CD pipeline
- **Amazon ECR** — Container image registry
- **Python/Flask** — EKS Status Hub app (tracks live status of K8s components)
- **Gunicorn** — Production WSGI server
- **Checkov** — Terraform and Kubernetes security scanning
- **Grype** — Vulnerability scanning
- **pre-commit** — Git hooks for code quality

## EKS Status Hub App

A Python/Flask platform status page that tracks the live health of Kubernetes components by calling the Kubernetes API from inside the cluster.

- Queries the K8s API for each component's deployment status
- Displays `Healthy` (green), `Degraded` (red), or `Unknown` (yellow) per component
- RBAC-scoped service account — only has `get` and `list` permissions on deployments
- Served by Gunicorn behind NGINX Ingress with TLS
- `/health` endpoint for Kubernetes liveness and readiness probes

## Architecture

![Architecture Diagram](images/architecture.png)

## Infrastructure

| Component | Details |
|-----------|---------|
| Cluster | EKS v1.31 |
| Region | eu-west-2 |
| VPC | 10.0.0.0/16 (3 AZs) |
| Worker Nodes | Managed node group (t3a.large / t3.large) |
| IRSA | cert-manager + external-dns |
| State | S3 backend |
| CI/CD | GitHub Actions (OIDC auth) |
| Container Registry | Amazon ECR |
| Monitoring | Prometheus + Grafana |

## Deployed Apps

- **ArgoCD** — `argocd.eiddev.xyz`
- **eks-status-hub** — `app-hub.eiddev.xyz`
- **Grafana** — `grafana.eiddev.xyz`

### EKS Status Hub
![EKS Status Hub](images/app-hub.png)

### ArgoCD
![ArgoCD](images/argocd.png)

### Grafana
![Grafana](images/grafana.png)

### EKS Status Hub — Degraded State
![Status Hub Degraded](images/app-hub-status-error.png)

## Usage

```bash
make init
make apply
make deploy
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make init` | Terraform init |
| `make plan` | Terraform plan |
| `make apply` | Terraform apply |
| `make destroy` | Terraform destroy |
| `make lint` | Terraform fmt + validate |
| `make sec` | Checkov + Grype scans |
| `make kubeconfig` | Update local kubeconfig |
| `make deploy` | Apply issuer + ArgoCD app |
| `make cleanup` | Run cleanup script |

## CI/CD Pipelines

Two separate pipelines:

**Infra Pipeline (`ci.yml`)** — triggers on changes to `terraform/`
- Pull requests → lint, security scan, terraform plan
- Push to main → plan job first, then apply job (requires plan to pass)

**Docker Pipeline (`docker.yml`)** — triggers on changes to `app/`
- Grype vulnerability scan
- Docker image build
- Push to Amazon ECR tagged with Git commit SHA
- Automatically updates image tag in `apps/app-hub.yml` and commits back to repo
- ArgoCD detects the change and deploys the new image automatically

Authentication via OIDC — no static credentials stored anywhere.

## Security

- Pre-commit hooks (YAML validation, Terraform fmt, Checkov)
- Checkov scanning (Terraform + Kubernetes)
- Grype vulnerability scanning on both Terraform and Docker image
- Hardened Kubernetes deployments (security context, resource limits, health probes, NetworkPolicy)
- Non-root container user (UID 10000)
- Immutable ECR image tags
- ECR images encrypted at rest with KMS

## What I Learnt

- How IRSA (IAM Roles for Service Accounts) works — linking Kubernetes service accounts to AWS IAM roles via OIDC so pods get scoped permissions without static credentials
- The importance of Helm dependency ordering — cert-manager CRDs must be installed before you can apply a ClusterIssuer, and external-dns needs its IRSA role ready before deployment
- How the full TLS flow works end-to-end: Ingress annotation → cert-manager picks it up → creates a Certificate resource → uses DNS-01 challenge via Route 53 → stores the cert in a Kubernetes Secret → NGINX serves it
- GitOps as a deployment model — ArgoCD reconciles cluster state with the Git repo, meaning the repo is the single source of truth
- How NetworkPolicies enforce pod-level traffic control — only allowing ingress from the nginx-ingress namespace to the app pod
- OIDC federation for CI/CD — GitHub Actions assumes an AWS role without any stored secrets, using short-lived tokens
- The value of security scanning in pipelines — Checkov catches Terraform misconfigs and Grype flags vulnerable dependencies before they reach the cluster
- How the Kubernetes API works as a REST API — making HTTP GET requests from inside a pod using a service account token to query deployment health
- RBAC in practice — scoping a service account to only the permissions it needs (get/list deployments) rather than cluster-wide access
- GitOps image tag automation — the CI pipeline commits the new image SHA back to the repo so ArgoCD can deploy without any manual steps

## Challenges Solved

- **Helm chart version conflicts** — Some chart versions had breaking changes or deprecated values. Had to pin versions (e.g. ArgoCD `5.19.15`, kube-prometheus-stack `84.3.0`) and cross-reference changelogs to get compatible configurations
- **cert-manager DNS-01 validation failing** — The IRSA role wasn't being assumed correctly because the service account annotation wasn't matching. Fixed by ensuring the namespace/service account pair in the IRSA module matched exactly what cert-manager deployed
- **external-dns not updating Route 53** — Permissions were correct but the hosted zone filter wasn't set, so external-dns was trying to manage zones it shouldn't. Adding the domain filter in the Helm values resolved it
- **Terraform dependency ordering** — Helm releases were attempting to deploy before the EKS cluster was fully ready. Solved by relying on implicit dependencies through the provider configuration and module outputs
- **GitHub Actions OIDC trust policy** — The IAM role's trust policy needed the exact GitHub repo and branch conditions. Debugging this required checking CloudTrail for `AssumeRoleWithWebIdentity` failures
- **Ingress not getting an external IP** — The NGINX ingress controller needed the AWS load balancer to provision in public subnets. Required correct subnet tagging (`kubernetes.io/role/elb = 1`) in the VPC Terraform config
- **EKS access entry conflicts** — The EKS Terraform module automatically creates a `cluster_creator` access entry which conflicted with manually defined entries, causing repeated pipeline failures. Fixed by setting `enable_cluster_creator_admin_permissions = false` and managing access entries explicitly
- **Terraform apply locking out cluster access** — Destroying the Admin access entry mid-apply caused kubectl to lose access. Recovered by manually recreating the access entry via AWS CLI and reimporting into Terraform state

## Cleanup

```bash
make cleanup
```
