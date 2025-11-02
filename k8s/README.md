# Kubernetes Deployment Commands for OCR PDF MCP Server

## Prerequisites
1. Ensure you have a Kubernetes cluster running
2. kubectl configured to connect to your cluster
3. Docker image built and pushed to a registry

## Build and Push Docker Image
```bash
# Build the image
docker build -t your-registry/ocr-pdf-mcp:latest .

# Push to registry
docker push your-registry/ocr-pdf-mcp:latest
```

## Deploy to Kubernetes
```bash
# Create namespace (optional)
kubectl create namespace ocr-pdf-mcp

# Apply all configurations
kubectl apply -f k8s/ -n ocr-pdf-mcp

# Or apply individually:
kubectl apply -f k8s/configmap.yaml -n ocr-pdf-mcp
kubectl apply -f k8s/deployment.yaml -n ocr-pdf-mcp
kubectl apply -f k8s/ingress.yaml -n ocr-pdf-mcp
kubectl apply -f k8s/hpa.yaml -n ocr-pdf-mcp
```

## Verify Deployment
```bash
# Check pods
kubectl get pods -n ocr-pdf-mcp

# Check services
kubectl get svc -n ocr-pdf-mcp

# Check ingress
kubectl get ingress -n ocr-pdf-mcp

# View logs
kubectl logs -f deployment/ocr-pdf-mcp -n ocr-pdf-mcp
```

## Scale Deployment
```bash
# Manual scaling
kubectl scale deployment ocr-pdf-mcp --replicas=5 -n ocr-pdf-mcp

# Check HPA status
kubectl get hpa -n ocr-pdf-mcp
```

## Update Deployment
```bash
# Update image
kubectl set image deployment/ocr-pdf-mcp ocr-pdf-mcp=your-registry/ocr-pdf-mcp:v1.1.0 -n ocr-pdf-mcp

# Check rollout status
kubectl rollout status deployment/ocr-pdf-mcp -n ocr-pdf-mcp
```

## Clean Up
```bash
# Delete all resources
kubectl delete -f k8s/ -n ocr-pdf-mcp

# Delete namespace
kubectl delete namespace ocr-pdf-mcp
```