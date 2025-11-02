#!/usr/bin/env python3
"""
Test Script for MCP Protocol Compliant Server

Tests all MCP endpoints and functionalities dengan proper validation.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any
import aiohttp
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServerTester:
    """Comprehensive MCP Server Test Suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_server_health(self) -> bool:
        """Test server health endpoint"""
        try:
            logger.info("🔍 Testing server health...")
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check passed: {data}")
                    self.test_results.append(("Health Check", True, data))
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
                    self.test_results.append(("Health Check", False, f"Status: {response.status}"))
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            self.test_results.append(("Health Check", False, str(e)))
            return False
    
    async def test_server_info(self) -> bool:
        """Test server info endpoint"""
        try:
            logger.info("🔍 Testing server info...")
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Server info: {data}")
                    self.test_results.append(("Server Info", True, data))
                    return True
                else:
                    logger.error(f"❌ Server info failed: {response.status}")
                    self.test_results.append(("Server Info", False, f"Status: {response.status}"))
                    return False
        except Exception as e:
            logger.error(f"❌ Server info error: {e}")
            self.test_results.append(("Server Info", False, str(e)))
            return False
    
    async def test_mcp_initialize(self) -> bool:
        """Test MCP initialize endpoint"""
        try:
            logger.info("🔍 Testing MCP initialize...")
            payload = {
                "jsonrpc": "2.0",
                "id": "test-init-1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "Test Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/mcp/initialize",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ MCP initialize success: {data}")
                    self.test_results.append(("MCP Initialize", True, data))
                    return True
                else:
                    text = await response.text()
                    logger.error(f"❌ MCP initialize failed: {response.status} - {text}")
                    self.test_results.append(("MCP Initialize", False, f"Status: {response.status}"))
                    return False
                    
        except Exception as e:
            logger.error(f"❌ MCP initialize error: {e}")
            self.test_results.append(("MCP Initialize", False, str(e)))
            return False
    
    async def test_tools_list(self) -> bool:
        """Test tools list endpoint"""
        try:
            logger.info("🔍 Testing tools list...")
            payload = {
                "jsonrpc": "2.0",
                "id": "test-tools-1",
                "method": "tools/list",
                "params": {}
            }
            
            async with self.session.post(
                f"{self.base_url}/mcp/tools/list",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Tools list success: {len(data.get('result', {}).get('tools', []))} tools found")
                    logger.info(f"Tools: {[tool.get('name') for tool in data.get('result', {}).get('tools', [])]}")
                    self.test_results.append(("Tools List", True, data))
                    return True
                else:
                    text = await response.text()
                    logger.error(f"❌ Tools list failed: {response.status} - {text}")
                    self.test_results.append(("Tools List", False, f"Status: {response.status}"))
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Tools list error: {e}")
            self.test_results.append(("Tools List", False, str(e)))
            return False
    
    async def test_tool_call(self) -> bool:
        """Test tool call endpoint"""
        try:
            logger.info("🔍 Testing tool call...")
            
            # Create a test PDF file path
            test_pdf_path = "test_document.pdf"
            
            payload = {
                "jsonrpc": "2.0",
                "id": "test-call-1",
                "method": "tools/call",
                "params": {
                    "name": "get_pdf_info",
                    "arguments": {
                        "pdf_path": test_pdf_path,
                        "analyze_content": True,
                        "check_ocr_needed": True
                    }
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/mcp/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ Tool call success")
                    logger.info(f"Result: {data.get('result', {}).get('content', [{}])[0].get('text', '')[:200]}...")
                    self.test_results.append(("Tool Call", True, data))
                    return True
                else:
                    text = await response.text()
                    logger.error(f"❌ Tool call failed: {response.status} - {text}")
                    self.test_results.append(("Tool Call", False, f"Status: {response.status}"))
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Tool call error: {e}")
            self.test_results.append(("Tool Call", False, str(e)))
            return False
    
    async def test_json_rpc(self) -> bool:
        """Test JSON-RPC endpoint"""
        try:
            logger.info("🔍 Testing JSON-RPC endpoint...")
            payload = {
                "jsonrpc": "2.0",
                "id": "test-jsonrpc-1",
                "method": "tools/list",
                "params": {}
            }
            
            async with self.session.post(
                f"{self.base_url}/jsonrpc",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ JSON-RPC endpoint success")
                    self.test_results.append(("JSON-RPC", True, data))
                    return True
                else:
                    text = await response.text()
                    logger.error(f"❌ JSON-RPC failed: {response.status} - {text}")
                    self.test_results.append(("JSON-RPC", False, f"Status: {response.status}"))
                    return False
                    
        except Exception as e:
            logger.error(f"❌ JSON-RPC error: {e}")
            self.test_results.append(("JSON-RPC", False, str(e)))
            return False
    
    async def test_tools_discovery(self) -> bool:
        """Test tools discovery endpoint"""
        try:
            logger.info("🔍 Testing tools discovery...")
            async with self.session.get(f"{self.base_url}/tools") as response:
                if response.status == 200:
                    data = await response.json()
                    tools_count = len(data.get('tools', []))
                    logger.info(f"✅ Tools discovery success: {tools_count} tools")
                    for tool in data.get('tools', []):
                        logger.info(f"  - {tool.get('name')}: {tool.get('description')}")
                    self.test_results.append(("Tools Discovery", True, data))
                    return True
                else:
                    logger.error(f"❌ Tools discovery failed: {response.status}")
                    self.test_results.append(("Tools Discovery", False, f"Status: {response.status}"))
                    return False
        except Exception as e:
            logger.error(f"❌ Tools discovery error: {e}")
            self.test_results.append(("Tools Discovery", False, str(e)))
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        logger.info("🚀 Starting MCP Server Test Suite")
        logger.info("="*60)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Server Info", self.test_server_info),
            ("MCP Initialize", self.test_mcp_initialize),
            ("Tools List", self.test_tools_list),
            ("Tool Call", self.test_tool_call),
            ("JSON-RPC", self.test_json_rpc),
            ("Tools Discovery", self.test_tools_discovery),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Running: {test_name}")
            try:
                result = await test_func()
                if result:
                    passed += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
        
        logger.info("\n" + "="*60)
        logger.info(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests PASSED! MCP server is working correctly.")
            return True
        else:
            logger.error(f"💥 {total - passed} tests FAILED!")
            return False
    
    def print_detailed_results(self):
        """Print detailed test results"""
        logger.info("\n" + "="*60)
        logger.info("📋 Detailed Test Results")
        logger.info("="*60)
        
        for test_name, success, result in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
            if not success:
                logger.info(f"    Error: {result}")
            elif isinstance(result, dict) and 'result' in result:
                logger.info(f"    Response: {json.dumps(result['result'], indent=2)[:200]}...")

async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", help="Server URL")
    parser.add_argument("--wait", type=int, default=2, help="Wait time before starting tests")
    
    args = parser.parse_args()
    
    # Wait for server to start
    if args.wait > 0:
        logger.info(f"⏳ Waiting {args.wait} seconds for server to start...")
        await asyncio.sleep(args.wait)
    
    async with MCPServerTester(args.url) as tester:
        success = await tester.run_all_tests()
        tester.print_detailed_results()
        
        if success:
            logger.info("\n🎉 MCP Server is ready for production!")
            sys.exit(0)
        else:
            logger.error("\n💥 MCP Server has issues that need to be fixed!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())