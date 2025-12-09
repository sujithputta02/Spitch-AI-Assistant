# Spitch AI Assistant - Quick Reference

## System Information Commands

### Ask for CPU Usage
**Command:** "what's my CPU usage?" or "cpu usage" or "system info"

**Response includes:**
- CPU percentage and core count
- Memory usage (percentage and GB)
- Disk usage (percentage and GB)  
- Network statistics (MB sent/received)

**Example:**
```
You: "what's my CPU usage?"
Spitch: "System Status: CPU 18.6% (8 cores), Memory 90.3% (5.3/5.9 GB), 
         Disk 2.8% (6.4/232.1 GB), Network sent 80.0 MB, received 524.5 MB"
```

### Specific Queries
- **"memory usage"** - Shows only memory information
- **"disk usage"** - Shows only disk information
- **"network stats"** - Shows only network information

## How It Works

1. **Direct Processing** - Your command is processed immediately for fast response
2. **MCP Integration** - Uses Model Context Protocol for enhanced capabilities
3. **Automatic Fallback** - If MCP fails, uses direct implementation
4. **Smart Detection** - Understands variations of your query

## Available MCP Operations

### System
- Get system information (CPU, memory, disk, network)
- Take screenshots
- Open applications

### Information
- Get current time and date
- Perform calculations
- Access learning data
- Search the web
- Get weather information

### Media
- Play music on Spotify
- Control playback

## Testing

Run comprehensive tests:
```bash
python test_system_commands.py   # Test system commands
python test_mcp_operations.py    # Test MCP operations
```

## Architecture

```
Your Command
    ↓
Direct Command Processor (Fast)
    ↓
MCP Client (Enhanced capabilities)
    ↓
MCP Server (Tool execution)
    ↓
Response to You
```

## Files Structure

```
engine/
├── command.py              # Command processing
├── advanced_features.py    # System info functions
├── mcp_client.py          # MCP client
├── mcp_operations.py      # MCP operation wrappers
└── ai_assistant.py        # AI processing

mcp_server.py              # MCP server
```

## Key Features

✅ **Comprehensive** - All system stats in one command
✅ **Fast** - Instant response with direct processing
✅ **Reliable** - Automatic fallback if MCP unavailable
✅ **Smart** - Understands natural language queries
✅ **Integrated** - Works with voice and text commands

---

**Ready to use!** Just ask "what's my CPU usage?" and get instant, comprehensive system information.
