"""
ReadPDFx - OCR PDF MCP Server

Production-ready MCP Protocol 2025-06-18 compliant server for OCR PDF processing.
"""

__version__ = "1.0.0"
__author__ = "ReadPDFx Team"

from .mcp_server import MCPServer
from .mcp_tools import MCPToolsRegistry
from .mcp_types import *
from .mcp_server_runner import MCPServerRunner

__all__ = [
    "MCPServer",
    "MCPToolsRegistry", 
    "MCPServerRunner",
    "MCP_PROTOCOL_VERSION",
    "MCPTool",
    "MCPToolResult",
    "MCPContent",
    "MCPTextContent"
]