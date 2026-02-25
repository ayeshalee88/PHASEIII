# TodoChatBot Helm Chart

Helm chart for deploying the TodoChatBot full-stack application (Frontend + Backend + PostgreSQL) to Kubernetes/Minikube.

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed
- [Helm 3](https://helm.sh/docs/intro/install/) installed
- Docker images built locally

## Quick Start

### 1. Start Minikube

```bash
minikube start --memory=4096 --cpus=2
```

### 2. Build and Load Docker Images

```bash
# Set Docker to use Minikube's daemon
eval $(minikube docker-env)

# Build backend image
docker build -t phase3-backend:latest -f backend/Dockerfile backend/

# Build frontend image
docker build -t phase3-frontend:latest -f frontend/Dockerfile frontend/
```

### 3. Install the Helm Chart

```bash
# Navigate to the chart directory
cd todochatbot

# Install the chart
helm install todochatbot . --namespace todochatbot --create-namespace
```

### 4. Access the Application

```bash
# Get frontend URL
minikube service todochatbot-frontend --url -n todochatbot

# Or open in browser
minikube service todochatbot-frontend -n todochatbot
```

### 5. Port Forward Services (Optional)

```bash
# Backend API
kubectl port-forward svc/todochatbot-backend 8000:8000 -n todochatbot

# Frontend
kubectl port-forward svc/todochatbot-frontend 3000:3000 -n todochatbot

# PostgreSQL
kubectl port-forward svc/todochatbot-postgresql 5432:5432 -n todochatbot
```

## Configuration

See `values.yaml` for all configurable parameters.

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable PostgreSQL database | `true` |
| `postgresql.auth.postgresPassword` | PostgreSQL password | `postgres` |
| `backend.enabled` | Enable backend service | `true` |
| `backend.image.repository` | Backend image name | `phase3-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `frontend.enabled` | Enable frontend service | `true` |
| `frontend.image.repository` | Frontend image name | `phase3-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.service.nodePort` | NodePort for frontend access | `30080` |

## Upgrade

```bash
helm upgrade todochatbot . --namespace todochatbot
```

## Uninstall

```bash
helm uninstall todochatbot --namespace todochatbot
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n todochatbot
kubectl describe pod <pod-name> -n todochatbot
```

### View Logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -n todochatbot -f

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -n todochatbot -f

# PostgreSQL logs
kubectl logs -l app.kubernetes.io/component=database -n todochatbot -f
```

### Reset Minikube

```bash
minikube delete
minikube start --memory=4096 --cpus=2
```

## Architecture

```
┌─────────────────┐
│   Frontend      │  Port 3000 (NodePort: 30080)
│   (Next.js)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Backend       │  Port 8000
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  Port 5432
│   (Database)    │
└─────────────────┘
```
