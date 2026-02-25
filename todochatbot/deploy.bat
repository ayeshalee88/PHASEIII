@echo off
REM Helm Deployment Script for TodoChatBot on Minikube (Windows)
REM Usage: deploy.bat

setlocal enabledelayedexpansion

set NAMESPACE=todochatbot
set RELEASE_NAME=todochatbot
set CHART_DIR=%~dp0

echo === TodoChatBot Helm Deployment ===
echo.

REM Check if Minikube is running
minikube status | findstr "host: Running" >nul
if errorlevel 1 (
    echo Starting Minikube...
    minikube start --memory=4096 --cpus=2
)

REM Set Docker environment to Minikube
echo.
echo Setting Docker environment to Minikube...
FOR /f "tokens=*" %%i IN ('minikube docker-env --shell cmd') DO %%i

REM Build Docker images
echo.
echo Building backend image...
docker build -t phase3-backend:latest -f backend/Dockerfile backend/

echo.
echo Building frontend image...
docker build -t phase3-frontend:latest -f frontend/Dockerfile frontend/

REM Create namespace if not exists
echo.
echo Creating namespace: %NAMESPACE%...
kubectl create namespace %NAMESPACE% --dry-run=client -o yaml | kubectl apply -f -

REM Install or upgrade Helm chart
echo.
echo Deploying Helm chart...
helm status %RELEASE_NAME% -n %NAMESPACE% >nul 2>&1
if errorlevel 1 (
    echo Installing new release...
    helm install %RELEASE_NAME% %CHART_DIR% --namespace %NAMESPACE% --create-namespace
) else (
    echo Upgrading existing release...
    helm upgrade %RELEASE_NAME% %CHART_DIR% --namespace %NAMESPACE%
)

REM Wait for pods to be ready
echo.
echo Waiting for pods to be ready...
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=%RELEASE_NAME% -n %NAMESPACE% --timeout=300s

REM Display status
echo.
echo === Deployment Complete ===
echo.
echo Services:
kubectl get svc -l app.kubernetes.io/instance=%RELEASE_NAME% -n %NAMESPACE%
echo.
echo Pods:
kubectl get pods -l app.kubernetes.io/instance=%RELEASE_NAME% -n %NAMESPACE%
echo.
echo Access the application:
FOR /f "tokens=*" %%i IN ('minikube service %RELEASE_NAME%-frontend --url -n %NAMESPACE%') DO echo   Frontend URL: %%i
echo   Or run: minikube service %RELEASE_NAME%-frontend -n %NAMESPACE%
echo.

endlocal
