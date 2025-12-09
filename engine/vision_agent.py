"""
Vision Agent - Eyes for Spitch
Handles screen capture and visual analysis using Gemini Vision.
part of Production-Grade Upgrade (Phase 7).
"""
import base64
import io
import os
import time
from typing import Dict, Any, Optional

try:
    import pyautogui
    from PIL import Image
    VISION_DEPS_AVAILABLE = True
except ImportError:
    VISION_DEPS_AVAILABLE = False
    print("[VisionAgent] Warning: pyautogui/PIL not installed. Vision features disabled.")

from engine.skill_registry import skill_registry
from engine.google_gemini import spitch_gemini

class VisionAgent:
    def __init__(self):
        self.screenshots_dir = "memory/screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self._register_skills()
        
    def _register_skills(self):
        """Register vision capabilities"""
        skill_registry.register_skill(
            "capture_screen",
            "Take a screenshot of the current screen",
            {"filename": "Optional filename (default: timestamp)"}
        )(self.capture_screen_action)
        
        skill_registry.register_skill(
            "analyze_screen",
            "Look at the screen and answer a question",
            {"query": "Question about what's on screen (e.g., 'describe this', 'fix this error')"}
        )(self.analyze_screen_action)

    def capture_screen_action(self, filename: str = None) -> str:
        """Capture full screen and save to disk"""
        if not VISION_DEPS_AVAILABLE:
            return "Error: Vision dependencies not installed."
            
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
            
        path = os.path.join(self.screenshots_dir, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        print(f"[VisionAgent] Screenshot saved to {path}")
        return path

    def analyze_screen_action(self, query: str) -> str:
        """Analyze the current screen using Gemini Vision"""
        if not VISION_DEPS_AVAILABLE:
            return "Error: Vision dependencies missing."
            
        # 1. Capture screen
        path = self.capture_screen_action()
        if path.startswith("Error"):
            return path
            
        print(f"[VisionAgent] Analyzing screen with query: '{query}'...")
        
        # 2. Prepare for Gemini (Gemini API handles images differently based on implementation)
        # Assuming spitch_gemini has a method for multi-modal or we add one.
        # For now, we'll try to use the existing process_query if it supports it, 
        # or we'll need to extend spitch_gemini.
        
        try:
            # We need to extend Gemini wrapper to support images.
            # Loading image bytes
            with open(path, "rb") as image_file:
                image_data = image_file.read()
                
            response = spitch_gemini.process_vision_query(query, image_data)
            return response
        except AttributeError:
             return "Error: Gemini wrapper needs update for Vision support."
        except Exception as e:
            return f"Vision analysis failed: {e}"

# Global instance
vision_agent = VisionAgent()
