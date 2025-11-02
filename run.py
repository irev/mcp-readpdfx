#!/usr/bin/env python3
"""
Simple OCR PDF MCP Server Runner
Quick start script for OCR PDF MCP server with production defaults.
"""

import sys
import asyncio
from pathlib import Path
from src.mcp_server_runner import MCPServerRunner
from dotenv import load_dotenv
import os

# Add project root and src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# try:
    # from src.mcp_server_runner import MCPServerRunner
# except ImportError:
    # If relative import fails, try absolute import  
    #from mcp_server_runner import MCPServerRunner

def main():
    """Start OCR PDF MCP server with production settings."""
    try:
        # Load environment variables
        
        load_dotenv()
        
        # Get host and port from environment variables with defaults
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "8000"))
        
        runner = MCPServerRunner(host=host, port=port)
        asyncio.run(runner.start_server())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()