#!/usr/bin/env python3
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"status": "working"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    print("Starting minimal server...")
    app.run(host="0.0.0.0", port=8083, debug=False)
