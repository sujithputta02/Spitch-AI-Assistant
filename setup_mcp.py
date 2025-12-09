#!/usr/bin/env python3
"""
Setup script for SPITCH MCP integration
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install MCP dependencies"""
    print("📦 Installing MCP dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_mcp.txt"
        ])
        print("✅ MCP dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def test_mcp_server():
    """Test if MCP server can start"""
    print("\n🧪 Testing MCP server...")
    
    try:
        # Try to import MCP
        import mcp
        print("✅ MCP SDK is available")
        
        # Check if server file exists
        if os.path.exists("mcp_server.py"):
            print("✅ MCP server file found")
        else:
            print("❌ MCP server file not found")
            return False
        
        # Check if client file exists
        if os.path.exists("engine/mcp_client.py"):
            print("✅ MCP client file found")
        else:
            print("❌ MCP client file not found")
            return False
        
        print("✅ MCP setup is complete!")
        return True
        
    except ImportError:
        print("❌ MCP SDK not installed properly")
        return False

def main():
    print("🚀 SPITCH MCP Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed!")
        return
    
    # Test MCP
    if not test_mcp_server():
        print("\n⚠️ MCP setup incomplete, but you can still use SPITCH without MCP features")
        return
    
    print("\n" + "=" * 50)
    print("🎉 MCP Setup Complete!")
    print("\nTo use MCP features:")
    print("1. Start SPITCH normally: python app.py")
    print("2. MCP will automatically enhance AI responses")
    print("3. View MCP tools: python mcp_server.py --list-tools")
    print("\nMCP provides:")
    print("  • Real-time system information")
    print("  • Enhanced calculations")
    print("  • Application control")
    print("  • Screenshot capabilities")
    print("  • And more!")

if __name__ == "__main__":
    main()
