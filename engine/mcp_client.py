"""
MCP Client for SPITCH AI Assistant
Connects to MCP server to access enhanced tools and capabilities
"""

import json
import subprocess
import asyncio
from typing import Dict, Any, List, Optional

class MCPClient:
    def __init__(self):
        self.server_process = None
        self.available_tools = []
        self.connected = False
        
    async def connect(self):
        """Connect to MCP server"""
        try:
            # Start MCP server process
            self.server_process = subprocess.Popen(
                ['python', 'mcp_server.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for server to start
            await asyncio.sleep(1)
            
            # List available tools
            await self.list_tools()
            
            self.connected = True
            print("✅ Connected to MCP server")
            return True
            
        except Exception as e:
            print(f"❌ Could not connect to MCP server: {e}")
            self.connected = False
            return False
    
    async def list_tools(self):
        """Get list of available tools from MCP server"""
        try:
            # In a real implementation, this would use the MCP protocol
            # For now, we'll use the predefined tools
            self.available_tools = [
                # Original tools
                "get_current_time",
                "search_web",
                "get_weather",
                "open_application",
                "play_music",
                "get_system_info",
                "take_screenshot",
                "calculate",
                # File System Operations
                "read_file",
                "write_file",
                "delete_file",
                "list_directory",
                "create_directory",
                "move_file",
                "copy_file",
                # Process Management
                "list_processes",
                "kill_process",
                "start_process",
                # System Control
                "set_volume",
                "get_volume",
                "shutdown_system",
                "lock_screen",
                # Clipboard Operations
                "get_clipboard",
                "set_clipboard",
                # Window Management
                "list_windows",
                "focus_window",
                "minimize_window",
                "close_window",
                # Network Operations
                "check_internet",
                "ping_host",
                # Automation
                "type_text",
                "press_key",
                "execute_command"
            ]
            return self.available_tools
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the MCP server"""
        try:
            # In a real implementation, this would use the MCP protocol
            # For now, we'll simulate tool calls
            
            if tool_name == "get_current_time":
                from datetime import datetime
                time_format = arguments.get("format", "12h")
                now = datetime.now()
                if time_format == "12h":
                    return f"Current time: {now.strftime('%I:%M %p')}, Date: {now.strftime('%B %d, %Y')}"
                else:
                    return f"Current time: {now.strftime('%H:%M')}, Date: {now.strftime('%Y-%m-%d')}"
            
            elif tool_name == "calculate":
                expression = arguments.get("expression", "")
                try:
                    # Safe evaluation
                    result = eval(expression, {"__builtins__": {}}, {})
                    return f"{expression} = {result}"
                except:
                    return f"Could not calculate: {expression}"
            
            elif tool_name == "get_system_info":
                try:
                    import platform
                    import psutil
                    
                    # CPU information
                    cpu_percent = psutil.cpu_percent(interval=1)
                    cpu_count = psutil.cpu_count()
                    
                    # Memory information
                    memory = psutil.virtual_memory()
                    memory_used_gb = memory.used / (1024**3)
                    memory_total_gb = memory.total / (1024**3)
                    
                    # Disk information
                    disk = psutil.disk_usage('/')
                    disk_used_gb = disk.used / (1024**3)
                    disk_total_gb = disk.total / (1024**3)
                    
                    # Network information
                    net_io = psutil.net_io_counters()
                    bytes_sent_mb = net_io.bytes_sent / (1024**2)
                    bytes_recv_mb = net_io.bytes_recv / (1024**2)
                    
                    return f"System Status: CPU {cpu_percent}% ({cpu_count} cores), Memory {memory.percent}% ({memory_used_gb:.1f}/{memory_total_gb:.1f} GB), Disk {disk.percent}% ({disk_used_gb:.1f}/{disk_total_gb:.1f} GB), Network sent {bytes_sent_mb:.1f} MB, received {bytes_recv_mb:.1f} MB"
                except Exception as e:
                    return f"System information not available: {str(e)}"
            
            elif tool_name == "get_learning_data":
                try:
                    import os
                    if os.path.exists("spitch_conversations.json"):
                        with open("spitch_conversations.json", 'r') as f:
                            data = json.load(f)
                        prefs = data.get('preferences', {})
                        return f"User preferences: {json.dumps(prefs)}"
                    return "No learning data available"
                except:
                    return "Could not read learning data"
            
            else:
                return f"Tool {tool_name} not implemented yet"
                
        except Exception as e:
            return f"Error calling tool: {str(e)}"
    
    def get_tools_description(self) -> str:
        """Get description of available tools for AI context"""
        if not self.available_tools:
            return ""
        
        tools_desc = "\n\nAvailable Tools (via MCP):\n"
        tools_desc += "# Basic Tools\n"
        tools_desc += "- get_current_time: Get current date and time\n"
        tools_desc += "- calculate: Perform mathematical calculations\n"
        tools_desc += "- get_system_info: Get system information (CPU, memory, disk)\n"
        tools_desc += "- open_application: Open applications\n"
        tools_desc += "- play_music: Play music on Spotify\n"
        tools_desc += "- search_web: Search the web\n"
        tools_desc += "- get_weather: Get weather information\n"
        tools_desc += "- take_screenshot: Capture screen\n\n"
        
        tools_desc += "# File System Operations\n"
        tools_desc += "- read_file: Read file contents\n"
        tools_desc += "- write_file: Write/create files\n"
        tools_desc += "- delete_file: Delete files\n"
        tools_desc += "- list_directory: List directory contents\n"
        tools_desc += "- create_directory: Create folders\n"
        tools_desc += "- move_file: Move/rename files\n"
        tools_desc += "- copy_file: Copy files\n\n"
        
        tools_desc += "# Process Management\n"
        tools_desc += "- list_processes: List all running processes\n"
        tools_desc += "- kill_process: Terminate processes\n"
        tools_desc += "- start_process: Start new processes\n\n"
        
        tools_desc += "# System Control\n"
        tools_desc += "- set_volume: Set system volume (0-100)\n"
        tools_desc += "- get_volume: Get current volume level\n"
        tools_desc += "- shutdown_system: Shutdown/restart/sleep PC\n"
        tools_desc += "- lock_screen: Lock the computer\n\n"
        
        tools_desc += "# Clipboard Operations\n"
        tools_desc += "- get_clipboard: Get clipboard contents\n"
        tools_desc += "- set_clipboard: Copy text to clipboard\n\n"
        
        tools_desc += "# Window Management\n"
        tools_desc += "- list_windows: List all open windows\n"
        tools_desc += "- focus_window: Bring window to front\n"
        tools_desc += "- minimize_window: Minimize a window\n"
        tools_desc += "- close_window: Close a window\n\n"
        
        tools_desc += "# Network Operations\n"
        tools_desc += "- check_internet: Check internet connectivity\n"
        tools_desc += "- ping_host: Ping a host\n\n"
        
        tools_desc += "# Automation\n"
        tools_desc += "- type_text: Type text using keyboard\n"
        tools_desc += "- press_key: Press keyboard keys\n"
        tools_desc += "- execute_command: Execute system commands\n"
        
        return tools_desc
    
    def disconnect(self):
        """Disconnect from MCP server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
        self.connected = False
        print("🔌 Disconnected from MCP server")

# Global MCP client instance
mcp_client = MCPClient()
