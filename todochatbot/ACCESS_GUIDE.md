# TodoChatBot - Minikube Deployment Access Guide

## ✅ Deployment Status

All services are running successfully on Minikube!

| Component | Pod Status | Service | Port |
|-----------|-----------|---------|------|
| **Frontend** | ✅ Running | NodePort | 30080 |
| **Backend** | ✅ Running | ClusterIP | 8000 |
| **PostgreSQL** | ✅ Running | ClusterIP | 5432 |

---

## 🔌 How to Access the Application

### Option 1: Port-Forwarding (Recommended for Windows/Docker driver)

**Start port-forwarding for Frontend:**
```powershell
kubectl port-forward svc/todochatbot-frontend 3000:3000 -n todochatbot
```
Then visit: **http://localhost:3000**

**Start port-forwarding for Backend:**
```powershell
kubectl port-forward svc/todochatbot-backend 8000:8000 -n todochatbot
```
Then visit: **http://localhost:8000**

**Start port-forwarding for PostgreSQL:**
```powershell
kubectl port-forward svc/todochatbot-postgresql 5432:5432 -n todochatbot
```
Connection string: `postgresql://postgres:postgres@localhost:5432/todoapp`

---

### Option 2: Minikube Service Command (Requires terminal to stay open)

```powershell
# Frontend
minikube service todochatbot-frontend -n todochatbot

# Backend
minikube service todochatbot-backend -n todochatbot
```

> ⚠️ **Note for Windows Docker driver**: The terminal must remain open for the service to be accessible.

---

### Option 3: Direct NodePort Access (If Minikube IP is accessible)

```powershell
# Get Minikube IP
minikube ip

# Access frontend directly
http://192.168.49.2:30080
```

---

## 🚀 Quick Start Commands

### Start All Port-Forwards (in separate terminals)

**Terminal 1 - Frontend:**
```powershell
kubectl port-forward svc/todochatbot-frontend 3000:3000 -n todochatbot
```

**Terminal 2 - Backend:**
```powershell
kubectl port-forward svc/todochatbot-backend 8000:8000 -n todochatbot
```

**Terminal 3 - Database (if needed):**
```powershell
kubectl port-forward svc/todochatbot-postgresql 5432:5432 -n todochatbot
```

---

## 📊 Useful Commands

```powershell
# Check all pods
kubectl get pods -n todochatbot

# Check all services
kubectl get svc -n todochatbot

# View frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -n todochatbot -f

# View backend logs
kubectl logs -l app.kubernetes.io/component=backend -n todochatbot -f

# View database logs
kubectl logs -l app.kubernetes.io/component=database -n todochatbot -f

# Restart a deployment
kubectl rollout restart deployment/todochatbot-frontend -n todochatbot
kubectl rollout restart deployment/todochatbot-backend -n todochatbot

# Uninstall everything
helm uninstall todochatbot -n todochatbot
```

---

## 🛠️ Troubleshooting

### Frontend not loading?
1. Check pod status: `kubectl get pods -n todochatbot`
2. View logs: `kubectl logs -l app.kubernetes.io/component=frontend -n todochatbot`
3. Restart: `kubectl rollout restart deployment/todochatbot-frontend -n todochatbot`

### Backend API errors?
1. Check if database is ready: `kubectl get pods -n todochatbot`
2. View backend logs: `kubectl logs -l app.kubernetes.io/component=backend -n todochatbot`
3. Verify DATABASE_URL is correct in deployment

### Minikube service not working?
This is a known issue with Docker driver on Windows. Use port-forwarding instead:
```powershell
kubectl port-forward svc/todochatbot-frontend 3000:3000 -n todochatbot
```

---

## 📝 Application Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js web application |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Swagger/OpenAPI documentation |
| PostgreSQL | localhost:5432 | Database (via port-forward) |

---

## 🎯 Current Configuration

- **Namespace**: todochatbot
- **Release**: todochatbot
- **Frontend**: NodePort 30080 (accessible via port-forward on 3000)
- **Backend**: ClusterIP 8000 (accessible via port-forward)
- **Database**: StatefulSet with 1Gi persistent storage

---

**Last Updated**: 2026-02-25
**Chart Version**: 0.2.0
**App Version**: 1.0.0
