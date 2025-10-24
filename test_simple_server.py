#!/usr/bin/env python3
"""
Simple test server to debug the connection issues.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    """Test endpoint."""
    return jsonify({"status": "working", "message": "Simple server is running"})

@app.route("/health", methods=["GET"])
def health():
    """Health check."""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    print("Starting simple test server...")
    app.run(host="0.0.0.0", port=8081, debug=False)