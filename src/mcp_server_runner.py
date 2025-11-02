#!/usr/bin/env python3
"""
MCP Protocol Compliant Server Runner

Production-ready MCP server yang mengikuti standard MCP Protocol 2025-06-18
dengan proper endpoints, error handling, dan structure yang rapi.
"""

import asyncio
import logging
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Import MCP components
from .mcp_server import MCPServer
from .mcp_tools import MCPToolsRegistry
# Note: SSEToolsProvider moved to backup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPServerRunner:
    """Production MCP Server Runner dengan HTTP endpoints"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        
        # Initialize components
        self.tools_registry = MCPToolsRegistry()
        self.mcp_server = MCPServer(
            server_name="OCR PDF MCP Server",
            server_version="1.0.0",
            description="MCP Protocol compliant server for OCR PDF processing"
        )
        self.mcp_server.set_tools_registry(self.tools_registry)
        
        # Skip SSE provider for now (has complex dependencies)
        self.sse_provider = None
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="OCR PDF MCP Server",
            description="MCP Protocol compliant server for OCR PDF processing",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all MCP standard routes"""
        
        # Health check
        @self.app.get("/")
        async def root():
            """Root endpoint with proper HTML and favicon"""
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>ReadPDFx - OCR PDF MCP Server</title>
                <link rel="icon" type="image/x-icon" href="/favicon.ico">
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .logo { text-align: center; margin-bottom: 30px; }
                    .logo img { max-width: 200px; height: auto; }
                    h1 { color: #333; text-align: center; }
                    .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .endpoints { background: #f3e5f5; padding: 15px; border-radius: 5px; }
                    .endpoint { margin: 5px 0; font-family: monospace; }
                    a { color: #1976d2; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="logo">
                        <img src="/logo.png" alt="ReadPDFx Logo" />
                    </div>
                    <h1>ReadPDFx - OCR PDF MCP Server</h1>
                    
                    <div class="info">
                        <strong>Status:</strong> Running<br>
                        <strong>Version:</strong> 1.0.0<br>
                        <strong>Protocol:</strong> MCP 2025-06-18<br>
                        <strong>Repository:</strong> <a href="https://github.com/irev/mcp-readpdfx" target="_blank">github.com/irev/mcp-readpdfx</a>
                    </div>
                    
                    <div class="endpoints">
                        <h3>Available Endpoints:</h3>
                        <div class="endpoint">• <a href="/health">GET /health</a> - Health check</div>
                        <div class="endpoint">• <a href="/docs">GET /docs</a> - API documentation</div>
                        <div class="endpoint">• POST /mcp/initialize - Initialize MCP session</div>
                        <div class="endpoint">• POST /mcp/tools/list - List available tools</div>
                        <div class="endpoint">• POST /mcp/tools/call - Call MCP tools</div>
                        <div class="endpoint">• GET /mcp/manifest - Get MCP manifest</div>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": "2025-01-12T11:00:00Z"}
        
        # Static files - favicon and logo
        @self.app.get("/favicon.ico")
        async def favicon():
            """Serve favicon.ico"""
            favicon_path = Path(__file__).parent.parent / "favicon.ico"
            if favicon_path.exists():
                return FileResponse(favicon_path, media_type="image/x-icon")
            else:
                raise HTTPException(status_code=404, detail="Favicon not found")
        
        @self.app.get("/logo.png")
        async def logo():
            """Serve logo.png"""
            logo_path = Path(__file__).parent.parent / "logo.png"
            if logo_path.exists():
                return FileResponse(logo_path, media_type="image/png")
            else:
                raise HTTPException(status_code=404, detail="Logo not found")
        
        # MCP Protocol endpoints
        @self.app.post("/mcp/initialize")
        async def mcp_initialize(request: Request):
            """MCP Initialize endpoint"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_initialize(body)
                return response
            except Exception as e:
                logger.error(f"Initialize error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mcp/tools/list")
        async def mcp_list_tools(request: Request):
            """MCP Tools List endpoint"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_tools_list(body)
                return response
            except Exception as e:
                logger.error(f"List tools error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mcp/tools/call")
        async def mcp_call_tool(request: Request):
            """MCP Tool Call endpoint"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_tools_call(body)
                return response
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # SSE endpoints for real-time updates
        @self.app.get("/sse/tools")
        async def sse_tools_stream():
            """SSE endpoint for tools updates"""
            # Simple SSE implementation - can be expanded later
            return {"message": "SSE tools stream not yet implemented"}
        
        @self.app.get("/sse/status")
        async def sse_status_stream():
            """SSE endpoint for status updates"""
            # Simple SSE implementation - can be expanded later
            return {"message": "SSE status stream not yet implemented"}
        
        # Tools discovery endpoints
        @self.app.get("/tools")
        async def get_tools():
            """Get all available tools (non-MCP endpoint for debugging)"""
            tools = self.tools_registry.list_tools()
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema.__dict__
                    }
                    for tool in tools
                ]
            }
        
        @self.app.get("/tools/{tool_name}")
        async def get_tool_info(tool_name: str):
            """Get specific tool information"""
            tool = self.tools_registry.get_tool(tool_name)
            if not tool:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
            return {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema.__dict__
            }
        
        # JSON-RPC endpoint (alternative to individual endpoints)
        @self.app.post("/jsonrpc")
        async def jsonrpc_handler(request: Request):
            """JSON-RPC 2.0 endpoint for MCP protocol"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_jsonrpc(body)
                return response
            except Exception as e:
                logger.error(f"JSON-RPC error: {e}")
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    },
                    "id": body.get("id") if isinstance(body, dict) else None
                }
    
    async def start_server(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP Server on {self.host}:{self.port}")
        logger.info("Available endpoints:")
        logger.info("  - GET  /                 - Server info")
        logger.info("  - GET  /health           - Health check")
        logger.info("  - POST /mcp/initialize   - MCP Initialize")
        logger.info("  - POST /mcp/tools/list   - MCP List Tools")
        logger.info("  - POST /mcp/tools/call   - MCP Call Tool")
        logger.info("  - POST /jsonrpc          - JSON-RPC 2.0")
        logger.info("  - GET  /sse/tools        - SSE Tools Stream")
        logger.info("  - GET  /sse/status       - SSE Status Stream")
        logger.info("  - GET  /tools            - Tools Discovery")
        logger.info("  - GET  /docs             - API Documentation")
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OCR PDF MCP Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run server
    server_runner = MCPServerRunner(host=args.host, port=args.port)
    
    try:
        asyncio.run(server_runner.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()