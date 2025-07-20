import openai
import os
import json
import re
import sys
from typing import Dict, Any, Optional

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check for valid OpenAI API key (optional fallback)
def get_openai_api_key():
    """Get OpenAI API key from config or environment"""
    try:
        from config import OPENAI_API_KEY
        if OPENAI_API_KEY and OPENAI_API_KEY != 'your-openai-api-key-here':
            return OPENAI_API_KEY
    except ImportError:
        pass
    
    # Try environment variable
    env_key = os.environ.get('OPENAI_API_KEY')
    if env_key and env_key != 'your-openai-api-key-here':
        return env_key
    
    return None

OPENAI_API_KEY = get_openai_api_key()
OPENAI_AVAILABLE = OPENAI_API_KEY is not None

if OPENAI_AVAILABLE:
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI API configured (fallback)")
    except Exception as e:
        print(f"❌ OpenAI configuration error: {e}")
        OPENAI_AVAILABLE = False
else:
    print("⚠️ OpenAI API key not configured - using Ollama as primary AI")
    client = None

# Import Ollama integration
try:
    from engine.ollama_integration import spitch_ollama
    OLLAMA_AVAILABLE = True
    print("✅ Ollama integration available")
    from config import OLLAMA_DEFAULT_MODEL, OLLAMA_TIMEOUT
except ImportError:
    OLLAMA_AVAILABLE = False
    print("❌ Ollama integration not available")

class SpitchAI:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """You are Spitch, an intelligent AI assistant that can help users with various tasks. You have the following capabilities:

1. **Music Control**: Play songs on Spotify, control playback, search for music
2. **System Operations**: Open applications, get system info, take screenshots
3. **Web Searches**: Search the internet, find information
4. **Conversation**: Answer questions, provide information, chat naturally
5. **Time & Date**: Tell time, date, set reminders
6. **Calculations**: Perform mathematical calculations
7. **Weather**: Get weather information
8. **General Knowledge**: Answer questions about any topic

When a user asks you to do something, extract the intent and provide a clear response. For music requests, be specific about what you're going to play.

Always be helpful, friendly, and conversational like Siri or Google Assistant. Keep responses concise but informative."""

    def process_command(self, user_input: str, speak_func=None, system_prompt_override: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user input and return intent and response
        
        Args:
            user_input: The user's command
            speak_func: The function to use for speaking
            system_prompt_override: A temporary system prompt for special cases
            model: The specific AI model to use for this query
        """
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})

            ai_response_text = None
            ai_source = "None"

            # Always use tinyllama unless a different model is explicitly specified
            model_to_use = model if model else OLLAMA_DEFAULT_MODEL

            # Try Ollama first (primary AI service)
            if OLLAMA_AVAILABLE and spitch_ollama.test_connection():
                try:
                    print("🔄 Using Ollama for AI processing...")
                    ai_response_text = spitch_ollama.process_query(
                        user_input, 
                        timeout=OLLAMA_TIMEOUT, 
                        system_prompt_override=system_prompt_override,
                        model=model_to_use
                    )
                    ai_source = "Ollama"
                except Exception as ollama_error:
                    print(f"❌ Ollama error: {ollama_error}")

            # Fallback to OpenAI if Ollama failed
            if not ai_response_text and OPENAI_AVAILABLE and client:
                # This part can be enhanced similarly if needed
                print(">> OpenAI fallback logic is not fully implemented in this version.")


            # If all AI services fail, use a simple fallback
            if not ai_response_text:
                return {
                    "intent": {"type": "fallback", "action_required": False},
                    "response": "I'm sorry, I'm having trouble processing that right now. Could you try again?",
                    "ai_source": "Error"
                }
            
            # --- New Intent Processing Logic ---
            try:
                # Assume the response is JSON and try to parse it
                intent = json.loads(ai_response_text)
                # If parsing succeeds, we have a command intent.
                # Generate a user-friendly response based on the intent.
                response_for_user = self._create_confirmation_response(intent)
                print(f"✅ Parsed AI intent (JSON): {intent}")

            except json.JSONDecodeError:
                # If parsing fails, it's a conversational response.
                intent = {"type": "conversation", "action_required": False}
                response_for_user = ai_response_text
                print(f"✅ Received conversational AI response: {response_for_user}")

            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response_for_user})

            return {
                "intent": intent,
                "response": response_for_user,
                "ai_source": ai_source
            }

        except Exception as e:
            print(f"❌ AI processing error: {e}")
            return {
                "intent": {"type": "fallback", "action_required": False},
                "response": "I'm sorry, an unexpected error occurred. Please try again.",
                "ai_source": "Error"
            }

    def _create_confirmation_response(self, intent: Dict[str, Any]) -> str:
        """Create a user-friendly confirmation message from an intent object."""
        intent_type = intent.get("type")
        if intent_type == "music_play":
            song = intent.get('song_name', 'that song')
            return f"Okay, playing {song} on Spotify."
        elif intent_type == "open_app":
            app = intent.get('app_name', 'the application')
            return f"Sure, opening {app}."
        elif intent_type == "web_search":
            term = intent.get('search_term', 'that')
            return f"Searching the web for {term}."
        else:
            # Generic fallback for other intent types
            return "Okay, on it."

    def _get_fallback_response(self, user_input: str) -> str:
        """Get a fallback response when AI services are unavailable"""
        user_input_lower = user_input.lower()
        
        # Quick responses for common queries
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Spitch, your AI assistant. I'm here to help you with various tasks."
        
        elif any(word in user_input_lower for word in ['time', 'what time']):
            return "I can tell you the current time. Let me check that for you."
        
        elif any(word in user_input_lower for word in ['date', 'what date', 'today']):
            return "I can tell you today's date. Let me check that for you."
        
        elif any(word in user_input_lower for word in ['weather', 'temperature']):
            return "I can help you check the weather. Let me get that information for you."
        
        elif any(word in user_input_lower for word in ['play', 'music', 'song', 'spotify']):
            return "I can help you play music on Spotify. What would you like to listen to?"
        
        elif any(word in user_input_lower for word in ['open', 'launch', 'start']):
            return "I can help you open applications. What would you like me to open?"
        
        elif any(word in user_input_lower for word in ['search', 'find', 'google']):
            return "I can help you search the web. What would you like me to search for?"
        
        elif any(word in user_input_lower for word in ['joke', 'funny']):
            return "I'd love to tell you a joke! Let me find a good one for you."
        
        elif any(word in user_input_lower for word in ['help', 'what can you do']):
            return "I can help you with many things: play music, open apps, search the web, tell time, check weather, take screenshots, and more. Just ask!"
        
        else:
            return "I understand you're asking about something, but I'm having trouble with my AI services right now. I can still help you with basic commands like opening apps, playing music, or checking the time."

    def _extract_intent(self, user_input: str, ai_response: str) -> Dict[str, Any]:
        """[DEPRECATED] This method is no longer the primary way to get intent."""
        print("Warning: _extract_intent is deprecated and should not be relied upon.")
        return {"type": "conversation"}

    def get_quick_response(self, user_input: str) -> str:
        """Get a quick response for simple queries without AI processing"""
        user_input_lower = user_input.lower()
        
        # Quick responses for common greetings
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you today?"
        
        elif any(word in user_input_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Have a great day!"
        
        elif any(word in user_input_lower for word in ['thanks', 'thank you']):
            return "You're welcome! Is there anything else I can help you with?"
        
        elif any(word in user_input_lower for word in ['how are you', 'how do you do']):
            return "I'm doing well, thank you for asking! How can I assist you?"
        
        return None  # No quick response available

# Create global instance
spitch_ai = SpitchAI() 