#!/usr/bin/env python3
"""
MCP stdio proxy for the YS Implementation Guides server.

Reads JSON-RPC from stdin, proxies to the remote HTTP MCP server
with automatic Google Cloud identity token authentication, and
writes responses to stdout.
"""

import sys
import json
import os
import time
import subprocess

import httpx

MCP_SERVER_URL = os.environ.get(
    "MCP_SERVER_URL",
    "https://mcp-server-375955300575.us-central1.run.app/mcp",
)


def get_identity_token() -> str:
    """Get a Google Cloud identity token for the MCP server using gcloud."""
    result = subprocess.run(
        ["gcloud", "auth", "print-identity-token", f"--audiences={MCP_SERVER_URL}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def proxy_request(request_data: dict, client: httpx.Client, token: str) -> dict:
    """Proxy a single JSON-RPC request to the remote MCP server."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    try:
        response = client.post(MCP_SERVER_URL, headers=headers, json=request_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": request_data.get("id"),
        }


def main():
    token = get_identity_token()
    token_time = time.monotonic()
    with httpx.Client(timeout=30.0) as client:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            # Refresh token every 45 minutes (they expire after 1 hour)
            if time.monotonic() - token_time > 2700:
                token = get_identity_token()
                token_time = time.monotonic()

            try:
                request_data = json.loads(line)
            except json.JSONDecodeError:
                error = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None,
                }
                print(json.dumps(error), flush=True)
                continue

            response_data = proxy_request(request_data, client, token)
            print(json.dumps(response_data), flush=True)


if __name__ == "__main__":
    main()
