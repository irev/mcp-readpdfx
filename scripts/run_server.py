#!/usr/bin/env python3
"""
OCR PDF MCP Server Runner with Development and Production modes.
Advanced script with configuration options for different environments.
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_server_runner import MCPServerRunner

def main():
    """Start OCR PDF MCP server with configurable settings."""
    parser = argparse.ArgumentParser(
        description="OCR PDF MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py                    # Production mode (default)
  python run_server.py --dev              # Development mode with debug
  python run_server.py --prod --port 9000 # Production mode on port 9000
  python run_server.py --dev --host 127.0.0.1 --port 8080  # Custom dev setup
        """
    )
    
    parser.add_argument(
        "--dev", 
        action="store_true",
        help="Enable development mode with debug logging"
    )
    parser.add_argument(
        "--prod", 
        action="store_true",
        help="Enable production mode (default)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    dev_mode = args.dev or not args.prod
    mode_name = "Development" if dev_mode else "Production"
    
    # Set logging level
    if dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    print("🚀 Starting OCR PDF MCP Server...")
    print("📖 Repository: https://github.com/irev/mcp-readpdfx")
    print(f"⚡ Mode: {mode_name}")
    print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
    print("📋 MCP Protocol endpoints:")
    print("   • GET  /health           - Health check")
    print("   • POST /mcp/initialize   - Initialize MCP session")
    print("   • POST /mcp/tools/list   - List available tools")
    print("   • POST /mcp/tools/call   - Call MCP tools")  
    print("   • GET  /mcp/manifest     - Get MCP manifest")
    print("   • GET  /docs             - API documentation")
    if dev_mode:
        print(" Debug logging: Enabled")
    print()
    
    # Create server runner
    server_runner = MCPServerRunner(host=args.host, port=args.port)
    
    try:
        asyncio.run(server_runner.start_server())
    except KeyboardInterrupt:
        print("\n⛔ Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()