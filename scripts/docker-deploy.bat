@echo off
REM OCR PDF MCP Server - Docker Build and Run Script (Windows)

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=ocr-pdf-mcp
set TAG=latest
set CONTAINER_NAME=ocr-pdf-mcp-server
set PORT=8000

echo 🐳 OCR PDF MCP Server - Docker Deployment
echo ========================================

REM Function to check if Docker is running
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)
echo ✅ Docker is running
goto :eof

REM Function to build Docker image
:build_image
echo 🔨 Building Docker image...

REM Use production Dockerfile if available, otherwise use standard
if exist "Dockerfile.prod" (
    set DOCKERFILE=Dockerfile.prod
    echo Using production Dockerfile
) else (
    set DOCKERFILE=Dockerfile
    echo Using standard Dockerfile
)

docker build -f %DOCKERFILE% -t %IMAGE_NAME%:%TAG% .
if errorlevel 1 (
    echo ❌ Docker build failed
    exit /b 1
)
echo ✅ Docker image built successfully
goto :eof

REM Function to cleanup existing container
:cleanup_container
docker ps -a --format "table {{.Names}}" | findstr /r "^%CONTAINER_NAME%$" >nul 2>&1
if not errorlevel 1 (
    echo 🧹 Stopping and removing existing container...
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
    echo ✅ Cleanup completed
)
goto :eof

REM Function to run Docker container
:run_container
echo 🚀 Starting container...

docker run -d ^
    --name %CONTAINER_NAME% ^
    -p %PORT%:8000 ^
    -e LOG_LEVEL=INFO ^
    -e CORS_ORIGINS=* ^
    -v "%cd%/pdf-test:/app/pdf-test:ro" ^
    -v "%cd%/logs:/app/logs" ^
    --restart unless-stopped ^
    %IMAGE_NAME%:%TAG%

if errorlevel 1 (
    echo ❌ Failed to start container
    exit /b 1
)

echo ✅ Container started successfully
echo 🌐 Server available at: http://localhost:%PORT%
echo 🏥 Health check: http://localhost:%PORT%/health
goto :eof

REM Function to show container logs
:show_logs
echo 📋 Container logs:
docker logs -f %CONTAINER_NAME%
goto :eof

REM Main execution
set ACTION=%1
if "%ACTION%"=="" set ACTION=run

if "%ACTION%"=="build" (
    call :check_docker
    call :build_image
) else if "%ACTION%"=="run" (
    call :check_docker
    call :build_image
    call :cleanup_container
    call :run_container
) else if "%ACTION%"=="start" (
    call :check_docker
    call :cleanup_container
    call :run_container
) else if "%ACTION%"=="stop" (
    echo 🛑 Stopping container...
    docker stop %CONTAINER_NAME%
    echo ✅ Container stopped
) else if "%ACTION%"=="logs" (
    call :show_logs
) else if "%ACTION%"=="clean" (
    echo 🧹 Cleaning up...
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
    docker rmi %IMAGE_NAME%:%TAG% >nul 2>&1
    echo ✅ Cleanup completed
) else if "%ACTION%"=="status" (
    echo 📊 Container status:
    docker ps -a --filter name=%CONTAINER_NAME% --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
) else (
    echo Usage: %0 {build^|run^|start^|stop^|logs^|clean^|status}
    echo.
    echo Commands:
    echo   build  - Build Docker image only
    echo   run    - Build and run container ^(default^)
    echo   start  - Start container ^(assumes image exists^)
    echo   stop   - Stop running container
    echo   logs   - Show container logs
    echo   clean  - Stop container and remove image
    echo   status - Show container status
    exit /b 1
)

endlocal