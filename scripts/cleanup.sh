#!/bin/bash
set -e

cd "$(dirname "$0")/.."

# 1. Delete ArgoCD apps
kubectl delete -f argocd/app-argo.yml --ignore-not-found

# 2. Delete app resources
kubectl delete -f apps/app-hub.yml -n my-app --ignore-not-found

# 3. Delete cert-manager CRDs
kubectl delete crd certificates.cert-manager.io --ignore-not-found
kubectl delete crd certificaterequests.cert-manager.io --ignore-not-found
kubectl delete crd clusterissuers.cert-manager.io --ignore-not-found
kubectl delete crd issuers.cert-manager.io --ignore-not-found
kubectl delete crd challenges.acme.cert-manager.io --ignore-not-found
kubectl delete crd orders.acme.cert-manager.io --ignore-not-found

# 4. Delete ArgoCD CRDs
kubectl delete crd applications.argoproj.io --ignore-not-found
kubectl delete crd applicationsets.argoproj.io --ignore-not-found
kubectl delete crd appprojects.argoproj.io --ignore-not-found

# 5. Delete namespaces
kubectl delete namespace argocd --ignore-not-found
kubectl delete namespace external-dns --ignore-not-found
kubectl delete namespace cert-manager --ignore-not-found
kubectl delete namespace ingress-nginx --ignore-not-found
kubectl delete namespace my-app --ignore-not-found

# 6. Wait for LB and DNS cleanup
echo "Waiting 60s for AWS resources to clean up..."
sleep 60

# 7. Destroy infrastructure (handles Helm releases, EKS, VPC, IAM)
terraform destroy -auto-approve
