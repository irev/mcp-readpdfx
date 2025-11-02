#!/usr/bin/env python3
"""
Start OCR PDF HTTP Server for ML Studio
Quick start script for HTTP server compatible with ML Studio and other HTTP clients.

Usage:
    python start_http_server.py
    python start_http_server.py --port 8000 --host 127.0.0.1
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are installed")
        return True
    except ImportError:
        print("❌ Missing HTTP server dependencies")
        print("Installing FastAPI and Uvicorn...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "python-multipart"], check=True)
            print("✅ HTTP server dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Start OCR PDF HTTP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--dev", action="store_true", help="Enable development mode with auto-reload")
    
    args = parser.parse_args()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        template_file = Path(".env.template")
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            print("✅ Created .env from template")
            print("📝 Please edit .env file to configure Tesseract path")
        else:
            print("❌ .env.template not found")
            print("Please create .env file with TESSERACT_PATH configuration")
    
    # Start HTTP server
    print(f"🚀 Starting OCR PDF HTTP Server...")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print(f"📚 Documentation: http://{args.host}:{args.port}/docs")
    print(f"🏥 Health Check: http://{args.host}:{args.port}/health")
    print("=" * 60)
    
    # Set environment variables
    os.environ["HTTP_HOST"] = args.host
    os.environ["HTTP_PORT"] = str(args.port)
    
    # Run the server
    cmd = [
        sys.executable, "http_server.py",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.dev:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()