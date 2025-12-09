"""
MCP Operations Wrapper
Provides easy access to MCP tools with fallback to direct implementations
"""

import asyncio
from typing import Optional, Dict, Any

def run_async_mcp(func, *args, **kwargs):
    """Helper to run async MCP functions"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(func(*args, **kwargs))
        loop.close()
        return result
    except Exception as e:
        print(f"❌ Async MCP error: {e}")
        return None

def mcp_get_system_info(speak_func=None) -> Optional[str]:
    """Get system info via MCP"""
    try:
        from engine.mcp_client import mcp_client
        result = run_async_mcp(mcp_client.call_tool, "get_system_info", {})
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP system info error: {e}")
        return None

def mcp_get_time(format="12h", speak_func=None) -> Optional[str]:
    """Get current time via MCP"""
    try:
        from engine.mcp_client import mcp_client
        result = run_async_mcp(mcp_client.call_tool, "get_current_time", {"format": format})
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP time error: {e}")
        return None

def mcp_calculate(expression: str, speak_func=None) -> Optional[str]:
    """Calculate via MCP"""
    try:
        from engine.mcp_client import mcp_client
        result = run_async_mcp(mcp_client.call_tool, "calculate", {"expression": expression})
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP calculate error: {e}")
        return None

def mcp_open_application(app_name: str, speak_func=None) -> Optional[str]:
    """Open application via MCP"""
    try:
        from engine.mcp_client import mcp_client
        result = run_async_mcp(mcp_client.call_tool, "open_application", {"app_name": app_name})
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP open app error: {e}")
        return None

def mcp_play_music(song_name: str, artist: str = "", speak_func=None) -> Optional[str]:
    """Play music via MCP"""
    try:
        from engine.mcp_client import mcp_client
        args = {"song_name": song_name}
        if artist:
            args["artist"] = artist
        result = run_async_mcp(mcp_client.call_tool, "play_music", args)
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP play music error: {e}")
        return None

def mcp_take_screenshot(filename: str = "", speak_func=None) -> Optional[str]:
    """Take screenshot via MCP"""
    try:
        from engine.mcp_client import mcp_client
        args = {"filename": filename} if filename else {}
        result = run_async_mcp(mcp_client.call_tool, "take_screenshot", args)
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP screenshot error: {e}")
        return None

def mcp_get_learning_data(speak_func=None) -> Optional[str]:
    """Get learning data via MCP"""
    try:
        from engine.mcp_client import mcp_client
        result = run_async_mcp(mcp_client.call_tool, "get_learning_data", {})
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP learning data error: {e}")
        return None

def mcp_search_web(query: str, speak_func=None) -> Optional[str]:
    """Search web via MCP"""
    try:
        from engine.mcp_client import mcp_client
        result = run_async_mcp(mcp_client.call_tool, "search_web", {"query": query})
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP search error: {e}")
        return None

def mcp_get_weather(location: str, speak_func=None) -> Optional[str]:
    """Get weather via MCP"""
    try:
        from engine.mcp_client import mcp_client
        result = run_async_mcp(mcp_client.call_tool, "get_weather", {"location": location})
        if result and speak_func:
            speak_func(result)
        return result
    except Exception as e:
        print(f"❌ MCP weather error: {e}")
        return None
