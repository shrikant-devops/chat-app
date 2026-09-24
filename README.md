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

