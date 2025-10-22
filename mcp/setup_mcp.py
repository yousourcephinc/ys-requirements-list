#!/usr/bin/env python3
"""
Setup script to install MCP for the Guides MCP Server.

This script helps in setting up the MCP server by installing the necessary dependencies.

Usage:
  python setup_mcp.py
"""

import subprocess
import sys
import os
import platform

def main():
    """Install MCP and other dependencies."""
    print("\n🚀 Setting up the Guides MCP Server...")
    
    # Check if MCP is already installed
    try:
        import mcp
        print("✅ MCP is already installed.")
    except ImportError:
        print("📦 Installing MCP...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp==0.1.0"])
            print("✅ MCP installed successfully.")
        except subprocess.CalledProcessError:
            print("❌ Failed to install MCP. Please install manually.")
            return False
    
    # Install other dependencies
    print("\n📦 Installing other dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please install manually.")
        return False
    
    print("\n✨ Setup completed successfully!")
    print("\nYou can now run the MCP server with:")
    print("  python guides_mcp.py")
    print("  or")
    print("  make mcp")
    print("\nTo test the MCP server, run:")
    print("  python test_guides_mcp.py")
    print("  or")
    print("  make test-mcp")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)