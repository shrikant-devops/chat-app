# Flask Chat App

A real-time chat app (Flask + Socket.IO + SQLite) built as a basic DevOps
practice project: containerized, tested in CI, and deployable to Kubernetes.

## Features

- Multi-room real-time chat over WebSockets (Socket.IO)
- Message history persisted in SQLite, replayed on join/reconnect
- `/health` (liveness) and `/ready` (readiness, checks DB) endpoints
- `/metrics` Prometheus endpoint (messages sent, connected clients, HTTP requests)
- Dockerfile, docker-compose, basic Kubernetes manifests
- GitHub Actions CI: lint (ruff) + tests (pytest) on every push/PR

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python wsgi.py
```

Open http://localhost:5000.

## Run with Docker

```bash
docker build -t flask-chat-app .
docker run -p 5000:5000 flask-chat-app
```

Or with Docker Compose:

```bash
docker compose up --build
```

## Run tests

```bash
pytest -v
```

## Deploy to Kubernetes

```bash
docker build -t flask-chat-app:latest .
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

The Service is a **NodePort**, so it's reachable from outside the cluster at
`http://<node-ip>:30500` — no port-forward needed.

- **minikube**: `minikube service flask-chat --url` prints the reachable URL
  (handles the node-ip lookup for you)
- **kind / bare-metal node**: `http://<node-ip>:30500`, where `<node-ip>` is
  from `kubectl get nodes -o wide`
- Still works locally too: `kubectl port-forward svc/flask-chat 5000:80`

## Project layout

```
app/
  __init__.py    app factory, config, extension wiring
  db.py          SQLite persistence
  events.py      Socket.IO event handlers (join/message/typing)
  routes.py      HTTP routes (index, health, ready, metrics, history API)
  metrics.py     Prometheus metric definitions
  templates/     index.html
  static/        chat.js, style.css
tests/           pytest suite (HTTP + Socket.IO)
k8s/             basic Deployment + Service
.github/workflows/ci.yml   lint + test
Dockerfile, docker-compose.yml
```

## Environment variables

See [.env.example](.env.example).

## Next steps to level this up

- Add a container registry push step to CI (build & push image on `main`)
- Add Redis so multiple app replicas can share chat traffic
- Swap SQLite for Postgres for real multi-replica deployments
- Add an Ingress to expose the app outside the cluster
- Wire `/metrics` into a Prometheus + Grafana stack
