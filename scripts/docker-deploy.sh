#!/bin/bash
# OCR PDF MCP Server - Docker Build and Run Script

set -e

# Configuration
IMAGE_NAME="ocr-pdf-mcp"
TAG="latest"
CONTAINER_NAME="ocr-pdf-mcp-server"
PORT="8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 OCR PDF MCP Server - Docker Deployment${NC}"
echo "========================================"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to build Docker image
build_image() {
    echo -e "${YELLOW}🔨 Building Docker image...${NC}"
    
    # Use production Dockerfile if available, otherwise use standard
    if [ -f "Dockerfile.prod" ]; then
        DOCKERFILE="Dockerfile.prod"
        echo "Using production Dockerfile"
    else
        DOCKERFILE="Dockerfile"
        echo "Using standard Dockerfile"
    fi
    
    docker build -f "$DOCKERFILE" -t "$IMAGE_NAME:$TAG" .
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
}

# Function to stop and remove existing container
cleanup_container() {
    if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${YELLOW}🧹 Stopping and removing existing container...${NC}"
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
        echo -e "${GREEN}✅ Cleanup completed${NC}"
    fi
}

# Function to run Docker container
run_container() {
    echo -e "${YELLOW}🚀 Starting container...${NC}"
    
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$PORT:8000" \
        -e LOG_LEVEL=INFO \
        -e CORS_ORIGINS="*" \
        -v "$(pwd)/pdf-test:/app/pdf-test:ro" \
        -v "$(pwd)/logs:/app/logs" \
        --restart unless-stopped \
        "$IMAGE_NAME:$TAG"
    
    echo -e "${GREEN}✅ Container started successfully${NC}"
    echo -e "${GREEN}🌐 Server available at: http://localhost:$PORT${NC}"
    echo -e "${GREEN}🏥 Health check: http://localhost:$PORT/health${NC}"
}

# Function to show container logs
show_logs() {
    echo -e "${YELLOW}📋 Container logs:${NC}"
    docker logs -f "$CONTAINER_NAME"
}

# Main execution
main() {
    case "${1:-run}" in
        "build")
            check_docker
            build_image
            ;;
        "run")
            check_docker
            build_image
            cleanup_container
            run_container
            ;;
        "start")
            check_docker
            cleanup_container
            run_container
            ;;
        "stop")
            echo -e "${YELLOW}🛑 Stopping container...${NC}"
            docker stop "$CONTAINER_NAME" || true
            echo -e "${GREEN}✅ Container stopped${NC}"
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            echo -e "${YELLOW}🧹 Cleaning up...${NC}"
            docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
            docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
            docker rmi "$IMAGE_NAME:$TAG" > /dev/null 2>&1 || true
            echo -e "${GREEN}✅ Cleanup completed${NC}"
            ;;
        "status")
            echo -e "${YELLOW}📊 Container status:${NC}"
            docker ps -a --filter name="$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            ;;
        *)
            echo "Usage: $0 {build|run|start|stop|logs|clean|status}"
            echo ""
            echo "Commands:"
            echo "  build  - Build Docker image only"
            echo "  run    - Build and run container (default)"
            echo "  start  - Start container (assumes image exists)"
            echo "  stop   - Stop running container"
            echo "  logs   - Show container logs"
            echo "  clean  - Stop container and remove image"
            echo "  status - Show container status"
            exit 1
            ;;
    esac
}

main "$@"