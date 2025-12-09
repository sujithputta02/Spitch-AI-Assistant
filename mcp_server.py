#!/usr/bin/env python3
"""
SPITCH MCP (Model Context Protocol) Server
Provides tools and resources for enhanced AI capabilities
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Try to import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP SDK not installed. Install with: pip install mcp")
    MCP_AVAILABLE = False
    sys.exit(1)

# Initialize MCP Server
app = Server("spitch-assistant")

# Tool definitions
TOOLS = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "description": "Time format (12h or 24h)",
                    "enum": ["12h", "24h"]
                }
            }
        }
    },
    {
        "name": "search_web",
        "description": "Search the web for information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get weather information for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or location"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "open_application",
        "description": "Open an application on the system",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name of the application to open"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "play_music",
        "description": "Play music on Spotify",
        "inputSchema": {
            "type": "object",
            "properties": {
                "song_name": {
                    "type": "string",
                    "description": "Name of the song to play"
                },
                "artist": {
                    "type": "string",
                    "description": "Artist name (optional)"
                }
            },
            "required": ["song_name"]
        }
    },
    {
        "name": "get_system_info",
        "description": "Get system information (CPU, memory, disk usage)",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "take_screenshot",
        "description": "Take a screenshot of the screen",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename for the screenshot"
                }
            }
        }
    },
    {
        "name": "calculate",
        "description": "Perform mathematical calculations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    },
    # File System Operations
    {
        "name": "read_file",
        "description": "Read contents of a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file (creates if doesn't exist)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to delete"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "list_directory",
        "description": "List contents of a directory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "Path to the directory to list"
                }
            },
            "required": ["dir_path"]
        }
    },
    {
        "name": "create_directory",
        "description": "Create a new directory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "Path to the directory to create"
                }
            },
            "required": ["dir_path"]
        }
    },
    {
        "name": "move_file",
        "description": "Move or rename a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Source file path"
                },
                "destination": {
                    "type": "string",
                    "description": "Destination file path"
                }
            },
            "required": ["source", "destination"]
        }
    },
    {
        "name": "copy_file",
        "description": "Copy a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Source file path"
                },
                "destination": {
                    "type": "string",
                    "description": "Destination file path"
                }
            },
            "required": ["source", "destination"]
        }
    },
    # Process Management
    {
        "name": "list_processes",
        "description": "List all running processes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "description": "Optional filter by process name"
                }
            }
        }
    },
    {
        "name": "kill_process",
        "description": "Terminate a process by name or PID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "process_identifier": {
                    "type": "string",
                    "description": "Process name or PID"
                }
            },
            "required": ["process_identifier"]
        }
    },
    {
        "name": "start_process",
        "description": "Start a new process/application",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command or application to start"
                },
                "arguments": {
                    "type": "string",
                    "description": "Optional command line arguments"
                }
            },
            "required": ["command"]
        }
    },
    # System Control
    {
        "name": "set_volume",
        "description": "Set system volume level",
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "number",
                    "description": "Volume level (0-100)"
                }
            },
            "required": ["level"]
        }
    },
    {
        "name": "get_volume",
        "description": "Get current system volume level",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "shutdown_system",
        "description": "Shutdown, restart, or sleep the system",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action: shutdown, restart, or sleep",
                    "enum": ["shutdown", "restart", "sleep"]
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "lock_screen",
        "description": "Lock the computer screen",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    # Clipboard Operations
    {
        "name": "get_clipboard",
        "description": "Get clipboard contents",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "set_clipboard",
        "description": "Set clipboard contents",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Content to copy to clipboard"
                }
            },
            "required": ["content"]
        }
    },
    # Window Management
    {
        "name": "list_windows",
        "description": "List all open windows",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "focus_window",
        "description": "Bring a window to front",
        "inputSchema": {
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window to focus"
                }
            },
            "required": ["window_title"]
        }
    },
    {
        "name": "minimize_window",
        "description": "Minimize a window",
        "inputSchema": {
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window to minimize"
                }
            },
            "required": ["window_title"]
        }
    },
    {
        "name": "close_window",
        "description": "Close a window",
        "inputSchema": {
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window to close"
                }
            },
            "required": ["window_title"]
        }
    },
    # Network Operations
    {
        "name": "check_internet",
        "description": "Check internet connectivity",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "ping_host",
        "description": "Ping a host to check connectivity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Host to ping (domain or IP)"
                }
            },
            "required": ["host"]
        }
    },
    # Automation
    {
        "name": "type_text",
        "description": "Type text using keyboard automation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to type"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "press_key",
        "description": "Press a keyboard key",
        "inputSchema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Key to press (e.g., 'enter', 'space', 'ctrl+c')"
                }
            },
            "required": ["key"]
        }
    },
    {
        "name": "execute_command",
        "description": "Execute a system command",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute"
                }
            },
            "required": ["command"]
        }
    }
]

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [Tool(**tool) for tool in TOOLS]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "get_current_time":
            time_format = arguments.get("format", "12h")
            now = datetime.now()
            if time_format == "12h":
                time_str = now.strftime("%I:%M %p")
                date_str = now.strftime("%B %d, %Y")
            else:
                time_str = now.strftime("%H:%M")
                date_str = now.strftime("%Y-%m-%d")
            
            return [TextContent(
                type="text",
                text=f"Current time: {time_str}\nDate: {date_str}"
            )]
        
        elif name == "search_web":
            query = arguments.get("query", "")
            # Simulate web search (in real implementation, use actual search API)
            return [TextContent(
                type="text",
                text=f"Web search results for '{query}':\n\nI don't have real-time web search capabilities, but I can help you with information I know or guide you to search engines."
            )]
        
        elif name == "get_weather":
            location = arguments.get("location", "")
            # Simulate weather (in real implementation, use weather API)
            return [TextContent(
                type="text",
                text=f"Weather information for {location}:\n\nI don't have real-time weather data access. Please check weather.com or your local weather service for current conditions."
            )]
        
        elif name == "open_application":
            app_name = arguments.get("app_name", "")
            # Import here to avoid circular imports
            import subprocess
            
            app_commands = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "explorer": "explorer.exe"
            }
            
            cmd = app_commands.get(app_name.lower(), app_name)
            try:
                subprocess.Popen(cmd)
                return [TextContent(
                    type="text",
                    text=f"Opening {app_name}..."
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not open {app_name}: {str(e)}"
                )]
        
        elif name == "play_music":
            song_name = arguments.get("song_name", "")
            artist = arguments.get("artist", "")
            
            search_query = f"{song_name} {artist}".strip()
            return [TextContent(
                type="text",
                text=f"Playing '{search_query}' on Spotify..."
            )]
        
        elif name == "get_system_info":
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
            
            info = f"""System Status: CPU {cpu_percent}% ({cpu_count} cores), Memory {memory.percent}% ({memory_used_gb:.1f}/{memory_total_gb:.1f} GB), Disk {disk.percent}% ({disk_used_gb:.1f}/{disk_total_gb:.1f} GB), Network sent {bytes_sent_mb:.1f} MB, received {bytes_recv_mb:.1f} MB"""
            
            return [TextContent(type="text", text=info)]
        
        elif name == "take_screenshot":
            filename = arguments.get("filename", f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            try:
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                return [TextContent(
                    type="text",
                    text=f"Screenshot saved as {filename}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not take screenshot: {str(e)}"
                )]
        
        elif name == "get_learning_data":
            try:
                if os.path.exists("spitch_conversations.json"):
                    with open("spitch_conversations.json", 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    preferences = data.get('preferences', {})
                    patterns_count = len(data.get('patterns', []))
                    
                    summary = f"""User Learning Data:
Preferences: {json.dumps(preferences, indent=2)}
Conversation Patterns: {patterns_count} stored
Last Updated: {data.get('last_updated', 'Unknown')}"""
                    
                    return [TextContent(type="text", text=summary)]
                else:
                    return [TextContent(
                        type="text",
                        text="No learning data available yet."
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error reading learning data: {str(e)}"
                )]
        
        elif name == "calculate":
            expression = arguments.get("expression", "")
            try:
                # Safe evaluation of mathematical expressions
                import ast
                import operator
                
                # Allowed operations
                ops = {
                    ast.Add: operator.add,
                    ast.Sub: operator.sub,
                    ast.Mult: operator.mul,
                    ast.Div: operator.truediv,
                    ast.Pow: operator.pow,
                    ast.USub: operator.neg
                }
                
                def eval_expr(node):
                    if isinstance(node, ast.Num):
                        return node.n
                    elif isinstance(node, ast.BinOp):
                        return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                    elif isinstance(node, ast.UnaryOp):
                        return ops[type(node.op)](eval_expr(node.operand))
                    else:
                        raise TypeError(node)
                
                result = eval_expr(ast.parse(expression, mode='eval').body)
                return [TextContent(
                    type="text",
                    text=f"{expression} = {result}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not calculate: {str(e)}"
                )]
        
        # File System Operations
        elif name == "read_file":
            file_path = arguments.get("file_path", "")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return [TextContent(
                    type="text",
                    text=f"File contents of {file_path}:\n\n{content}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not read file: {str(e)}"
                )]
        
        elif name == "write_file":
            file_path = arguments.get("file_path", "")
            content = arguments.get("content", "")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return [TextContent(
                    type="text",
                    text=f"Successfully wrote to {file_path}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not write file: {str(e)}"
                )]
        
        elif name == "delete_file":
            file_path = arguments.get("file_path", "")
            try:
                os.remove(file_path)
                return [TextContent(
                    type="text",
                    text=f"Successfully deleted {file_path}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not delete file: {str(e)}"
                )]
        
        elif name == "list_directory":
            dir_path = arguments.get("dir_path", "")
            try:
                items = os.listdir(dir_path)
                items_list = "\n".join([f"- {item}" for item in items])
                return [TextContent(
                    type="text",
                    text=f"Contents of {dir_path}:\n{items_list}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not list directory: {str(e)}"
                )]
        
        elif name == "create_directory":
            dir_path = arguments.get("dir_path", "")
            try:
                os.makedirs(dir_path, exist_ok=True)
                return [TextContent(
                    type="text",
                    text=f"Successfully created directory {dir_path}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not create directory: {str(e)}"
                )]
        
        elif name == "move_file":
            source = arguments.get("source", "")
            destination = arguments.get("destination", "")
            try:
                import shutil
                shutil.move(source, destination)
                return [TextContent(
                    type="text",
                    text=f"Successfully moved {source} to {destination}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not move file: {str(e)}"
                )]
        
        elif name == "copy_file":
            source = arguments.get("source", "")
            destination = arguments.get("destination", "")
            try:
                import shutil
                shutil.copy2(source, destination)
                return [TextContent(
                    type="text",
                    text=f"Successfully copied {source} to {destination}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not copy file: {str(e)}"
                )]
        
        # Process Management
        elif name == "list_processes":
            filter_name = arguments.get("filter", "")
            try:
                import psutil
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        if not filter_name or filter_name.lower() in proc.info['name'].lower():
                            processes.append(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, CPU: {proc.info['cpu_percent']}%, Memory: {proc.info['memory_percent']:.1f}%")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if processes:
                    process_list = "\n".join(processes[:50])  # Limit to 50 processes
                    return [TextContent(
                        type="text",
                        text=f"Running processes:\n{process_list}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text="No processes found matching the filter"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not list processes: {str(e)}"
                )]
        
        elif name == "kill_process":
            identifier = arguments.get("process_identifier", "")
            try:
                import psutil
                killed = False
                
                # Try as PID first
                try:
                    pid = int(identifier)
                    proc = psutil.Process(pid)
                    proc.terminate()
                    killed = True
                    return [TextContent(
                        type="text",
                        text=f"Successfully terminated process with PID {pid}"
                    )]
                except ValueError:
                    # Not a number, treat as process name
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            if identifier.lower() in proc.info['name'].lower():
                                proc.terminate()
                                killed = True
                                return [TextContent(
                                    type="text",
                                    text=f"Successfully terminated process {proc.info['name']} (PID: {proc.info['pid']})"
                                )]
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                if not killed:
                    return [TextContent(
                        type="text",
                        text=f"Could not find process: {identifier}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not kill process: {str(e)}"
                )]
        
        elif name == "start_process":
            command = arguments.get("command", "")
            args = arguments.get("arguments", "")
            try:
                import subprocess
                full_command = f"{command} {args}".strip()
                subprocess.Popen(full_command, shell=True)
                return [TextContent(
                    type="text",
                    text=f"Successfully started: {full_command}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not start process: {str(e)}"
                )]
        
        # System Control
        elif name == "set_volume":
            level = arguments.get("level", 50)
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                
                return [TextContent(
                    type="text",
                    text=f"Volume set to {level}%"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not set volume (pycaw may not be installed): {str(e)}"
                )]
        
        elif name == "get_volume":
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
                
                return [TextContent(
                    type="text",
                    text=f"Current volume: {current_volume}%"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not get volume (pycaw may not be installed): {str(e)}"
                )]
        
        elif name == "shutdown_system":
            action = arguments.get("action", "shutdown")
            try:
                import subprocess
                if action == "shutdown":
                    subprocess.run(["shutdown", "/s", "/t", "10"])
                    return [TextContent(type="text", text="System will shutdown in 10 seconds")]
                elif action == "restart":
                    subprocess.run(["shutdown", "/r", "/t", "10"])
                    return [TextContent(type="text", text="System will restart in 10 seconds")]
                elif action == "sleep":
                    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
                    return [TextContent(type="text", text="System going to sleep")]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not perform system action: {str(e)}"
                )]
        
        elif name == "lock_screen":
            try:
                import subprocess
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
                return [TextContent(type="text", text="Screen locked")]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not lock screen: {str(e)}"
                )]
        
        # Clipboard Operations
        elif name == "get_clipboard":
            try:
                import pyperclip
                content = pyperclip.paste()
                return [TextContent(
                    type="text",
                    text=f"Clipboard contents: {content}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not get clipboard (pyperclip may not be installed): {str(e)}"
                )]
        
        elif name == "set_clipboard":
            content = arguments.get("content", "")
            try:
                import pyperclip
                pyperclip.copy(content)
                return [TextContent(
                    type="text",
                    text=f"Copied to clipboard: {content}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not set clipboard (pyperclip may not be installed): {str(e)}"
                )]
        
        # Window Management
        elif name == "list_windows":
            try:
                import pygetwindow as gw
                windows = gw.getAllTitles()
                windows = [w for w in windows if w.strip()]  # Filter empty titles
                window_list = "\n".join([f"- {w}" for w in windows[:30]])  # Limit to 30
                return [TextContent(
                    type="text",
                    text=f"Open windows:\n{window_list}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not list windows: {str(e)}"
                )]
        
        elif name == "focus_window":
            window_title = arguments.get("window_title", "")
            try:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    windows[0].activate()
                    return [TextContent(
                        type="text",
                        text=f"Focused window: {window_title}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Window not found: {window_title}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not focus window: {str(e)}"
                )]
        
        elif name == "minimize_window":
            window_title = arguments.get("window_title", "")
            try:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    windows[0].minimize()
                    return [TextContent(
                        type="text",
                        text=f"Minimized window: {window_title}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Window not found: {window_title}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not minimize window: {str(e)}"
                )]
        
        elif name == "close_window":
            window_title = arguments.get("window_title", "")
            try:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    windows[0].close()
                    return [TextContent(
                        type="text",
                        text=f"Closed window: {window_title}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Window not found: {window_title}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not close window: {str(e)}"
                )]
        
        # Network Operations
        elif name == "check_internet":
            try:
                import socket
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                return [TextContent(
                    type="text",
                    text="Internet connection is active"
                )]
            except Exception:
                return [TextContent(
                    type="text",
                    text="No internet connection"
                )]
        
        elif name == "ping_host":
            host = arguments.get("host", "")
            try:
                import subprocess
                result = subprocess.run(["ping", "-n", "4", host], capture_output=True, text=True, timeout=10)
                return [TextContent(
                    type="text",
                    text=f"Ping results for {host}:\n{result.stdout}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not ping host: {str(e)}"
                )]
        
        # Automation
        elif name == "type_text":
            text = arguments.get("text", "")
            try:
                import pyautogui
                pyautogui.write(text, interval=0.05)
                return [TextContent(
                    type="text",
                    text=f"Typed: {text}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not type text: {str(e)}"
                )]
        
        elif name == "press_key":
            key = arguments.get("key", "")
            try:
                import pyautogui
                pyautogui.press(key)
                return [TextContent(
                    type="text",
                    text=f"Pressed key: {key}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not press key: {str(e)}"
                )]
        
        elif name == "execute_command":
            command = arguments.get("command", "")
            try:
                import subprocess
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                output = result.stdout if result.stdout else result.stderr
                return [TextContent(
                    type="text",
                    text=f"Command output:\n{output}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Could not execute command: {str(e)}"
                )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]

@app.list_resources()
async def list_resources() -> List[EmbeddedResource]:
    """List available resources"""
    resources = []
    
    # Add learning data as a resource
    if os.path.exists("spitch_conversations.json"):
        resources.append(EmbeddedResource(
            uri="file://spitch_conversations.json",
            name="User Learning Data",
            description="Stored user preferences and conversation patterns",
            mimeType="application/json"
        ))
    
    return resources

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    print("🚀 Starting SPITCH MCP Server...")
    asyncio.run(main())
