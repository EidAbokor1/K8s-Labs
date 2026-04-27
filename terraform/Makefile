CLUSTER_NAME = eks-labs
REGION       = eu-west-2

.PHONY: init plan destroy apply kubeconfig lint cleanup deploy sec

plan:
	terraform plan
init:
	terraform init
apply:
	terraform apply
destroy:
	terraform destroy
lint:
	terraform fmt -check
	terraform validate

kubeconfig:
	aws eks update-kubeconfig --name $(CLUSTER_NAME) --region $(REGION)
deploy:
	kubectl apply -f ../cert-man/issuer.yml
	kubectl apply -f ../argocd/app-argo.yml
sec:
	checkov -d .
	grype dir:..

cleanup:
	../scripts/cleanup.sh
