from flask import Flask, jsonify, render_template
from kubernetes import client, config

app = Flask(__name__)

config.load_incluster_config()

def get_deployment_status(namespace,deployment_name):
    try:
        v1=client.AppsV1Api()
        deployment = v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)

        if deployment.status.available_replicas > 0:
            return "Healthy"
        else:
            return "Degraded"
    except Exception:
        return "Unknown"

@app.route("/")
def home():
    components = [
    {
        "name": "NGINX Ingress Controller",
        "description": "Traffic routing and load balancing",
        "status": get_deployment_status("ingress-nginx", "ingress-nginx-controller"),
        "url": None,
    },
    {
        "name": "cert-manager",
        "description": "Automated TLS certificate provisioning",
        "status": get_deployment_status("cert-manager", "cert-manager"),
        "url": None,
    },
    {
        "name": "ExternalDNS",
        "description": "Syncs ingress hosts with Route 53",
        "status": get_deployment_status("external-dns", "external-dns"),
        "url": None,
    },
    {
        "name": "ArgoCD",
        "description": "GitOps continuous deployment",
        "status": get_deployment_status("argocd", "argo-cd-argocd-server"),
        "url": "https://argocd.eiddev.xyz",
    },
    {
        "name": "Prometheus",
        "description": "Cluster metrics collection",
        "status": get_deployment_status("monitoring", "kube-prometheus-stack-operator"),
        "url": None,
    },
    {
        "name": "Grafana",
        "description": "Metrics visualisation and dashboards",
        "status": get_deployment_status("monitoring", "kube-prometheus-stack-grafana"),
        "url": "https://grafana.eiddev.xyz",
    },
]

    return render_template('index.html', components=components)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
