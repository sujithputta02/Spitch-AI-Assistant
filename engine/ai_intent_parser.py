"""
AI-Powered Intent Parser - JARVIS-Level Natural Language Understanding

This module uses AI (Gemini/GPT) to parse natural language commands
and extract intent, entities, and action plans dynamically.
"""
import json
import re
from typing import Dict, Any, List, Optional

class AIIntentParser:
    def __init__(self, ai_assistant):
        """Initialize with AI assistant instance for Gemini/GPT access"""
        self.ai_assistant = ai_assistant
        
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input using AI to extract intent and generate action plan
        WITH SESSION CONTEXT AND MEMORY
        
        Returns:
        {
            'intent': 'primary_action',
            'entities': {'app': 'notepad', 'text': 'hello'},
            'actions': [
                {'type': 'open_app', 'params': {'app': 'notepad'}},
                {'type': 'type_text', 'params': {'text': 'hello'}}
            ],
            'confidence': 0.95
        }
        """
        
        # Import session manager and memory bank
        try:
            from engine.session_manager import session_manager
            from engine.memory_bank import memory_bank
            
            # Resolve pronouns using session context
            resolved_input = session_manager.resolve_pronoun(user_input)
            if resolved_input != user_input:
                print(f"[AIIntentParser] Resolved '{user_input}' to '{resolved_input}'")
                user_input = resolved_input
            
            # Get conversation context
            context = session_manager.get_context_for_prompt()
            
        except Exception as e:
            print(f"[AIIntentParser] Session/Memory not available: {e}")
            context = ""
        
        # Create AI prompt for intent extraction (with context)
        prompt = self._create_intent_prompt(user_input, context)
        
        try:
            # Use Gemini for intent parsing
            from engine.google_gemini import spitch_gemini
            
            response = spitch_gemini.process_query(
                prompt,
                timeout=10
            )
            
            if not response:
                print("[AIIntentParser] Gemini returned no response, using fallback")
                return self._fallback_parse(user_input)
            
            # Parse JSON response
            intent_data = self._parse_ai_response(response)
            
            return intent_data
            
        except Exception as e:
            print(f"[AIIntentParser] Error parsing intent: {e}")
            # Fallback to pattern-based parsing
            return self._fallback_parse(user_input)
    
    def _get_dynamic_skills_prompt(self) -> str:
        """Get the available skills formatted for the prompt"""
        try:
            from engine.skill_registry import skill_registry
            return skill_registry.generate_system_prompt_snippet()
        except ImportError:
            return "Available action types: open_app, type_text, open_website, calculate"

    def _create_intent_prompt(self, user_input: str, context: str = "") -> str:
        """Create prompt for AI to parse user intent WITH CONTEXT"""
        
        context_section = ""
        if context:
            context_section = f"""
Previous Conversation:
{context}

"""
        
        prompt = f"""{context_section}You are JARVIS, an intelligent AI assistant. Parse this user command and extract the intent and action plan.

User Command: "{user_input}"

Analyze the command and return a JSON object with:
1. "intent": Primary goal (e.g., "open_and_write", "search_web", "calculate", "control_system")
2. "entities": Extracted entities like app names, file names, text content, numbers, websites
3. "actions": Step-by-step action plan as array of objects with 'type' and 'params'
4. "confidence": Your confidence level (0.0-1.0)

Available action types:
- open_app (params: app)
- open_website (params: url)
- type_text (params: text)
- press_key (params: key)
- write_file (params: file_path, content)
- delete_file (params: file_path)
- rename_file (params: old_path, new_path)
- set_volume (params: level)
- take_screenshot (params: filename)
- calculate (params: expression)
- copy_to_clipboard (params: text)
- kill_process (params: process)

Examples:

User: "I want to write a shopping list"
{{
  "intent": "create_document",
  "entities": {{"document_type": "shopping list", "app": "notepad"}},
  "actions": [
    {{"type": "open_app", "params": {{"app": "notepad"}}}},
    {{"type": "type_text", "params": {{"text": "Shopping List:"}}}}
  ],
  "confidence": 0.9
}}

User: "Find Python tutorials"
{{
  "intent": "web_search",
  "entities": {{"query": "Python tutorials"}},
  "actions": [
    {{"type": "open_website", "params": {{"url": "https://www.google.com/search?q=Python+tutorials"}}}}
  ],
  "confidence": 0.95
}}

User: "What's 25 times 4?"
{{
  "intent": "calculate",
  "entities": {{"expression": "25*4"}},
  "actions": [
    {{"type": "calculate", "params": {{"expression": "25*4"}}}}
  ],
  "confidence": 1.0
}}

Now parse the user's command and return ONLY the JSON object, nothing else:"""

        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON"""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                intent_data = json.loads(json_str)
                return intent_data
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"[AIIntentParser] Error parsing AI response: {e}")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, user_input: str) -> Dict[str, Any]:
        """Fallback to simple pattern-based parsing"""
        user_lower = user_input.lower()
        
        # Simple pattern matching as fallback
        if 'search' in user_lower or 'find' in user_lower:
            query = re.sub(r'(search|find|for|on google|on web)', '', user_lower).strip()
            return {
                'intent': 'web_search',
                'entities': {'query': query},
                'actions': [
                    {'type': 'open_website', 'params': {'url': f'https://www.google.com/search?q={query}'}}
                ],
                'confidence': 0.6
            }
        
        elif 'calculate' in user_lower or 'what is' in user_lower or 'what\'s' in user_lower:
            expr_match = re.search(r'(?:calculate|what is|what\'s)\s+(.+)', user_lower)
            if expr_match:
                expression = expr_match.group(1).strip()
                return {
                    'intent': 'calculate',
                    'entities': {'expression': expression},
                    'actions': [
                        {'type': 'calculate', 'params': {'expression': expression}}
                    ],
                    'confidence': 0.7
                }
        
        elif 'in browser' in user_lower or 'website' in user_lower or any(app in user_lower for app in ['gemini', 'chatgpt', 'claude', 'youtube']):
            # specific website handling
            target = re.sub(r'(open|launch|start|in browser|website)', '', user_lower).strip()
            
            # Common mappings
            url_map = {
                'gemini': 'https://gemini.google.com',
                'chatgpt': 'https://chat.openai.com',
                'claude': 'https://claude.ai',
                'youtube': 'https://youtube.com',
                'google': 'https://google.com'
            }
            
            # Find best match
            url = f"https://{target}.com"
            for key, val in url_map.items():
                if key in target:
                    url = val
                    break
            
            return {
                'intent': 'open_website',
                'entities': {'url': url},
                'actions': [
                    {'type': 'open_website', 'params': {'url': url}}
                ],
                'confidence': 0.85
            }

        elif 'open' in user_lower:
            app_match = re.search(r'open\s+(\w+)', user_lower)
            if app_match:
                app = app_match.group(1)
                return {
                    'intent': 'open_app',
                    'entities': {'app': app},
                    'actions': [
                        {'type': 'open_app', 'params': {'app': app}}
                    ],
                    'confidence': 0.8
                }
        
        # Unknown intent
        return {
            'intent': 'unknown',
            'entities': {},
            'actions': [],
            'confidence': 0.0
        }

# Global instance (will be initialized with AI assistant)
ai_intent_parser = None

def initialize_parser(ai_assistant):
    """Initialize the global parser with AI assistant instance"""
    global ai_intent_parser
    ai_intent_parser = AIIntentParser(ai_assistant)
    return ai_intent_parser
