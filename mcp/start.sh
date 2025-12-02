#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
python3 -m gunicorn -w 1 -b 127.0.0.1:8080 --timeout 120 guides_mcp_http_server:app
