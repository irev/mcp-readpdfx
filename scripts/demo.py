#!/usr/bin/env python3
"""
Quick Start Script for OCR PDF MCP Server

Menjalankan MCP server dan test dalam satu command untuk demonstrasi cepat.
"""

import asyncio
import subprocess
import sys
import time
import logging
import signal
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerDemo:
    """Demo runner for MCP Server"""
    
    def __init__(self):
        self.server_process = None
        self.base_dir = Path(__file__).parent
    
    def check_dependencies(self):
        """Check if required files exist"""
        required_files = [
            "mcp_server_runner.py",
            "test_mcp_server.py",
            "mcp_types.py",
            "mcp_server.py",
            "mcp_tools.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.base_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"❌ Missing required files: {missing_files}")
            return False
        
        logger.info("✅ All required files found")
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        try:
            logger.info("📦 Installing dependencies...")
            
            # Check if requirements file exists
            req_files = ["requirements_new.txt", "requirements.txt"]
            req_file = None
            
            for req in req_files:
                if (self.base_dir / req).exists():
                    req_file = req
                    break
            
            if req_file:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", req_file
                ], check=True, capture_output=True)
                logger.info(f"✅ Dependencies installed from {req_file}")
            else:
                # Install essential dependencies manually
                essential_deps = [
                    "fastapi>=0.104.0",
                    "uvicorn[standard]>=0.24.0", 
                    "aiohttp>=3.9.0",
                    "pydantic>=2.5.0"
                ]
                
                for dep in essential_deps:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", dep
                    ], check=True, capture_output=True)
                
                logger.info("✅ Essential dependencies installed")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Dependency installation error: {e}")
            return False
    
    def start_server(self):
        """Start MCP server in background"""
        try:
            logger.info("🚀 Starting MCP Server on http://localhost:8000")
            
            # Start server process
            self.server_process = subprocess.Popen([
                sys.executable, "mcp_server_runner.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.base_dir)
            
            # Wait for server to start
            logger.info("⏳ Waiting for server to start...")
            time.sleep(3)
            
            # Check if process is still running
            if self.server_process.poll() is None:
                logger.info("✅ Server started successfully")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"❌ Server failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")
            return False
    
    def run_tests(self):
        """Run test suite"""
        try:
            logger.info("🧪 Running test suite...")
            
            # Run tests
            result = subprocess.run([
                sys.executable, "test_mcp_server.py", "--wait", "1"
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ All tests PASSED!")
                logger.info("\n" + result.stdout)
                return True
            else:
                logger.error("❌ Some tests FAILED!")
                logger.error("\n" + result.stderr)
                logger.info("\n" + result.stdout)
                return False
                
        except Exception as e:
            logger.error(f"❌ Test execution error: {e}")
            return False
    
    def stop_server(self):
        """Stop MCP server"""
        if self.server_process:
            logger.info("🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            logger.info("✅ Server stopped")
    
    def run_demo(self):
        """Run complete demo"""
        logger.info("🎬 Starting OCR PDF MCP Server Demo")
        logger.info("="*60)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Install dependencies if needed
        try:
            import fastapi
            import uvicorn
            import aiohttp
            logger.info("✅ Required packages already installed")
        except ImportError:
            logger.info("📦 Installing required packages...")
            if not self.install_dependencies():
                return False
        
        # Start server
        if not self.start_server():
            return False
        
        try:
            # Run tests
            test_success = self.run_tests()
            
            if test_success:
                logger.info("\n" + "="*60)
                logger.info("🎉 DEMO COMPLETED SUCCESSFULLY!")
                logger.info("🌐 Server is running at: http://localhost:8000")
                logger.info("📚 API docs available at: http://localhost:8000/docs")
                logger.info("🔧 Available endpoints:")
                logger.info("  - POST /mcp/initialize   - MCP Initialize")
                logger.info("  - POST /mcp/tools/list   - List Tools")
                logger.info("  - POST /mcp/tools/call   - Call Tool")
                logger.info("  - GET  /tools            - Tools Discovery")
                logger.info("  - GET  /health           - Health Check")
                logger.info("\n📄 Configuration files:")
                logger.info("  - mcp.json               - MCP Protocol definition")
                logger.info("  - package.json           - Node.js compatibility")  
                logger.info("  - pyproject.toml         - Python packaging")
                logger.info("  - mcp-config.yaml        - Deployment config")
                logger.info("\n💡 Press Ctrl+C to stop the server")
                
                # Keep server running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("\n👋 Demo stopped by user")
                
                return True
            else:
                logger.error("💥 Demo failed - please check the logs above")
                return False
                
        finally:
            self.stop_server()

def main():
    """Main entry point"""
    demo = MCPServerDemo()
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        logger.info("\n🛑 Stopping demo...")
        demo.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        success = demo.run_demo() 
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"💥 Demo error: {e}")
        demo.stop_server()
        sys.exit(1)

if __name__ == "__main__":
    main()