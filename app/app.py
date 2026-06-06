from flask import Flask, jsonify, render_template

app = Flask(__name__)

components = [
    {
        "name": "NGINX Ingress Controller",
        "description": "Traffic routing and load balancing",
        "status": "Healthy",
        "url": None,
    },
    {
        "name": "cert-manager",
        "description": "Automated TLS certificate provisioning",
        "status": "Healthy",
        "url": None,
    },
    {
        "name": "ExternalDNS",
        "description": "Syncs ingress hosts with Route 53",
        "status": "Healthy",
        "url": None,
    },
    {
        "name": "ArgoCD",
        "description": "GitOps continuous deployment",
        "status": "Healthy",
        "url": "https://argocd.eiddev.xyz",
    },
    {
        "name": "Prometheus",
        "description": "Cluster metrics collection",
        "status": "Healthy",
        "url": None,
    },
    {
        "name": "Grafana",
        "description": "Metrics visualisation and dashboards",
        "status": "Healthy",
        "url": "https://grafana.eiddev.xyz",
    },
]


@app.route("/")
def home():
    return render_template('index.html', components=components)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
