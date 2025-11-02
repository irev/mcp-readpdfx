#!/bin/bash
# OCR PDF MCP Server - Kubernetes Deployment Script

set -e

# Configuration
NAMESPACE="ocr-pdf-mcp"
IMAGE_NAME="ocr-pdf-mcp"
TAG="latest"
REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"  # Default to local registry

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}☸️  OCR PDF MCP Server - Kubernetes Deployment${NC}"
echo "=================================================="

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed${NC}"
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to build and push Docker image
build_and_push() {
    echo -e "${YELLOW}🔨 Building and pushing Docker image...${NC}"
    
    # Build image
    if [ -f "Dockerfile.prod" ]; then
        DOCKERFILE="Dockerfile.prod"
        echo "Using production Dockerfile"
    else
        DOCKERFILE="Dockerfile"
        echo "Using standard Dockerfile"
    fi
    
    docker build -f "$DOCKERFILE" -t "$REGISTRY/$IMAGE_NAME:$TAG" .
    
    # Push to registry
    docker push "$REGISTRY/$IMAGE_NAME:$TAG"
    
    echo -e "${GREEN}✅ Image built and pushed successfully${NC}"
}

# Function to create namespace
create_namespace() {
    echo -e "${YELLOW}📁 Creating namespace...${NC}"
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo -e "${BLUE}ℹ️  Namespace $NAMESPACE already exists${NC}"
    else
        kubectl create namespace "$NAMESPACE"
        echo -e "${GREEN}✅ Namespace $NAMESPACE created${NC}"
    fi
}

# Function to update image references in YAML files
update_image_refs() {
    echo -e "${YELLOW}🔄 Updating image references...${NC}"
    
    # Update deployment.yaml with correct image
    if [ -f "k8s/deployment.yaml" ]; then
        sed -i.bak "s|image: ocr-pdf-mcp:latest|image: $REGISTRY/$IMAGE_NAME:$TAG|g" k8s/deployment.yaml
        echo -e "${GREEN}✅ Updated deployment.yaml${NC}"
    fi
}

# Function to deploy to Kubernetes
deploy() {
    echo -e "${YELLOW}🚀 Deploying to Kubernetes...${NC}"
    
    # Apply configurations
    kubectl apply -f k8s/ -n "$NAMESPACE"
    
    echo -e "${GREEN}✅ Deployment applied successfully${NC}"
}

# Function to wait for deployment
wait_for_deployment() {
    echo -e "${YELLOW}⏳ Waiting for deployment to be ready...${NC}"
    
    kubectl rollout status deployment/ocr-pdf-mcp -n "$NAMESPACE" --timeout=300s
    
    echo -e "${GREEN}✅ Deployment is ready${NC}"
}

# Function to show deployment status
show_status() {
    echo -e "${YELLOW}📊 Deployment status:${NC}"
    echo ""
    
    echo -e "${BLUE}Pods:${NC}"
    kubectl get pods -n "$NAMESPACE" -o wide
    echo ""
    
    echo -e "${BLUE}Services:${NC}"
    kubectl get svc -n "$NAMESPACE"
    echo ""
    
    echo -e "${BLUE}Ingress:${NC}"
    kubectl get ingress -n "$NAMESPACE" 2>/dev/null || echo "No ingress found"
    echo ""
    
    echo -e "${BLUE}HPA:${NC}"
    kubectl get hpa -n "$NAMESPACE" 2>/dev/null || echo "No HPA found"
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}📋 Application logs:${NC}"
    kubectl logs -f deployment/ocr-pdf-mcp -n "$NAMESPACE"
}

# Function to port forward
port_forward() {
    echo -e "${YELLOW}🔌 Setting up port forwarding...${NC}"
    echo -e "${GREEN}🌐 Server will be available at: http://localhost:8000${NC}"
    echo -e "${BLUE}Press Ctrl+C to stop port forwarding${NC}"
    kubectl port-forward svc/ocr-pdf-mcp-service 8000:80 -n "$NAMESPACE"
}

# Function to scale deployment
scale_deployment() {
    local replicas=${2:-3}
    echo -e "${YELLOW}📈 Scaling deployment to $replicas replicas...${NC}"
    
    kubectl scale deployment ocr-pdf-mcp --replicas="$replicas" -n "$NAMESPACE"
    kubectl rollout status deployment/ocr-pdf-mcp -n "$NAMESPACE"
    
    echo -e "${GREEN}✅ Scaled to $replicas replicas${NC}"
}

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up resources...${NC}"
    
    kubectl delete -f k8s/ -n "$NAMESPACE" --ignore-not-found=true
    kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Function to restart deployment
restart_deployment() {
    echo -e "${YELLOW}🔄 Restarting deployment...${NC}"
    
    kubectl rollout restart deployment/ocr-pdf-mcp -n "$NAMESPACE"
    kubectl rollout status deployment/ocr-pdf-mcp -n "$NAMESPACE"
    
    echo -e "${GREEN}✅ Deployment restarted${NC}"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "build")
            check_prerequisites
            build_and_push
            ;;
        "deploy")
            check_prerequisites
            build_and_push
            create_namespace
            update_image_refs
            deploy
            wait_for_deployment
            show_status
            ;;
        "update")
            check_prerequisites
            build_and_push
            update_image_refs
            kubectl set image deployment/ocr-pdf-mcp ocr-pdf-mcp="$REGISTRY/$IMAGE_NAME:$TAG" -n "$NAMESPACE"
            wait_for_deployment
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "forward"|"port-forward")
            port_forward
            ;;
        "scale")
            scale_deployment "$@"
            ;;
        "restart")
            restart_deployment
            ;;
        "clean"|"cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 {build|deploy|update|status|logs|forward|scale|restart|cleanup}"
            echo ""
            echo "Commands:"
            echo "  build         - Build and push Docker image only"
            echo "  deploy        - Full deployment (build, push, deploy)"
            echo "  update        - Update existing deployment with new image"
            echo "  status        - Show deployment status"
            echo "  logs          - Show application logs"
            echo "  forward       - Port forward to local machine"
            echo "  scale [n]     - Scale deployment to n replicas (default: 3)"
            echo "  restart       - Restart deployment"
            echo "  cleanup       - Remove all resources"
            echo ""
            echo "Environment variables:"
            echo "  DOCKER_REGISTRY - Docker registry URL (default: localhost:5000)"
            exit 1
            ;;
    esac
}

main "$@"