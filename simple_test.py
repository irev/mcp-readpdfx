#!/usr/bin/env python3
"""
Simple test to check server endpoints
"""

import requests
import time

def test_endpoints():
    base_url = "http://localhost:8001"  # Try the original port
    
    endpoints = [
        "/health",
        "/api/version", 
        "/api/status",
        "/api/ping",
        "/mcp/manifest"
    ]
    
    print("🔍 Testing MCP server endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {data}")
                except:
                    print(f"   Response: {response.text[:100]}...")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection refused (server not running?)")
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint}: Timeout")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    # Test JSON-RPC ping
    try:
        ping_request = {
            "jsonrpc": "2.0",
            "method": "ping", 
            "id": 1
        }
        response = requests.post(f"{base_url}/jsonrpc", json=ping_request, timeout=10)
        print(f"✅ JSON-RPC ping: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ JSON-RPC ping: {e}")

if __name__ == "__main__":
    test_endpoints()