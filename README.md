
practice project: containerized, tested in CI, and deployable to Kubernetes.

## Features

- Multi-room real-time chat 
- Message history persisted in SQLite, replayed on join/reconnect
- `/health` (liveness) and `/ready` (readiness, checks DB) endpoints
- `/metrics` Prometheus endpoint (messages sent, connected clients, HTTP requests)
- Dockerfile, docker-compose, basic Kubernetes manifests
-

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


```

## Deploy to Kubernetes

```bash
docker build -t flask-chat-app:latest .
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

