#!/usr/bin/env python3
"""
Simple OCR PDF MCP Server Runner
Quick start script for OCR PDF MCP server with production defaults.
"""

import sys
import asyncio
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

from src.mcp_server_runner import MCPServerRunner

def main():
    """Start OCR PDF MCP server with production settings."""
    print("🚀 Starting OCR PDF MCP Server...")
    print("📖 Repository: https://github.com/irev/mcp-readpdfx")
    print("⚡ Mode: Production")
    print("🌐 Server will be available at: http://0.0.0.0:8000")
    print("📋 MCP Protocol endpoints:")
    print("   • GET  /health           - Health check")
    print("   • POST /mcp/initialize   - Initialize MCP session")
    print("   • POST /mcp/tools/list   - List available tools")
    print("   • POST /mcp/tools/call   - Call MCP tools")
    print("   • GET  /mcp/manifest     - Get MCP manifest")
    print("   • GET  /docs             - API documentation")
    print()
    
    # Create server runner
    server_runner = MCPServerRunner(host="0.0.0.0", port=8000)
    
    try:
        asyncio.run(server_runner.start_server())
    except KeyboardInterrupt:
        print("\n⛔ Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()