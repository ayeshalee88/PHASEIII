#!/bin/bash

# Helm Deployment Script for TodoChatBot on Minikube
# Usage: ./helm-deploy.sh

set -e

NAMESPACE="todochatbot"
RELEASE_NAME="todochatbot"
CHART_DIR="$(dirname "$0")"

echo "=== TodoChatBot Helm Deployment ==="
echo ""

# Check if Minikube is running
if ! minikube status | grep -q "host: Running"; then
    echo "Starting Minikube..."
    minikube start --memory=4096 --cpus=2
fi

# Set Docker environment to Minikube
echo "Setting Docker environment to Minikube..."
eval $(minikube docker-env)

# Build Docker images
echo ""
echo "Building backend image..."
docker build -t phase3-backend:latest -f backend/Dockerfile backend/

echo ""
echo "Building frontend image..."
docker build -t phase3-frontend:latest -f frontend/Dockerfile frontend/

# Create namespace if not exists
echo ""
echo "Creating namespace: $NAMESPACE..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade Helm chart
echo ""
echo "Deploying Helm chart..."
if helm status $RELEASE_NAME -n $NAMESPACE &> /dev/null; then
    echo "Upgrading existing release..."
    helm upgrade $RELEASE_NAME $CHART_DIR --namespace $NAMESPACE
else
    echo "Installing new release..."
    helm install $RELEASE_NAME $CHART_DIR --namespace $NAMESPACE --create-namespace
fi

# Wait for pods to be ready
echo ""
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE --timeout=300s

# Display status
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Services:"
kubectl get svc -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE
echo ""
echo "Pods:"
kubectl get pods -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE
echo ""
echo "Access the application:"
echo "  Frontend: $(minikube service $RELEASE_NAME-frontend --url -n $NAMESPACE)"
echo "  Or run: minikube service $RELEASE_NAME-frontend -n $NAMESPACE"
echo ""
