#!/usr/bin/env python3
"""
MCP HTTP Proxy for Claude Desktop

This script acts as a stdio-based MCP server that proxies requests to the HTTP MCP server.
This allows Claude Desktop to use the remote HTTP MCP server via stdio transport.
"""

import sys
import json
import asyncio
from typing import Any, Dict
import httpx

# Configuration
HTTP_MCP_URL = "https://mcp-server-375955300575.us-central1.run.app/mcp"
API_KEY = "test-key"

async def proxy_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Proxy a JSON-RPC request to the HTTP MCP server."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(HTTP_MCP_URL, headers=headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": request_data.get("id")
            }

async def main():
    """Main stdio loop for MCP communication."""
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            # Parse JSON-RPC request
            request_data = json.loads(line.strip())
            
            # Proxy to HTTP server
            response_data = await proxy_request(request_data)
            
            # Write response to stdout
            print(json.dumps(response_data), flush=True)
            
        except json.JSONDecodeError:
            # Invalid JSON
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                },
                "id": None
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            # Other errors
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": None
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())