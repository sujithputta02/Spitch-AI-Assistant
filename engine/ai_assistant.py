import openai
import os
import json
import re
import sys
import datetime
from typing import Dict, Any, Optional

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check for valid OpenAI/OpenRouter API key (optional fallback)
def get_api_key():
    """Get API key from config or environment"""
    try:
        from config import OPENAI_API_KEY, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL
        if OPENROUTER_API_KEY and OPENROUTER_API_KEY != 'your-openai-api-key-here':
            return OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL
        elif OPENAI_API_KEY and OPENAI_API_KEY != 'your-openai-api-key-here':
            return OPENAI_API_KEY, None, None
    except ImportError:
        pass
    
    # Try environment variable
    env_key = os.environ.get('OPENAI_API_KEY')
    if env_key and env_key != 'your-openai-api-key-here':
        return env_key, None, None
    
    return None, None, None

API_KEY, BASE_URL, MODEL_NAME = get_api_key()
API_AVAILABLE = API_KEY is not None

if API_AVAILABLE:
    try:
        if BASE_URL:  # OpenRouter
            client = openai.OpenAI(
                api_key=API_KEY,
                base_url=BASE_URL
            )
            print(f"[OK] OpenRouter API configured with model: {MODEL_NAME}")
        else:  # Standard OpenAI
            client = openai.OpenAI(api_key=API_KEY)
            MODEL_NAME = "gpt-3.5-turbo"
            print("[OK] OpenAI API configured (fallback)")
    except Exception as e:
        print(f"[ERROR] API configuration error: {e}")
        API_AVAILABLE = False
else:
    print("[WARNING] No API key configured - using Ollama as primary AI")
    client = None

# Import Ollama integration
try:
    from engine.ollama_integration import spitch_ollama
    OLLAMA_AVAILABLE = True
    print("[OK] Ollama integration available")
    from config import OLLAMA_DEFAULT_MODEL, OLLAMA_TIMEOUT
except ImportError:
    OLLAMA_AVAILABLE = False
    spitch_ollama = None
    OLLAMA_DEFAULT_MODEL = None
    OLLAMA_TIMEOUT = 15
    print("[ERROR] Ollama integration not available")

# Import Google Gemini integration
try:
    from engine.google_gemini import spitch_gemini
    GEMINI_AVAILABLE = True
    print("[OK] Google Gemini integration available")
except ImportError:
    GEMINI_AVAILABLE = False
    spitch_gemini = None
    print("[ERROR] Google Gemini integration not available")

class SpitchAI:
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.learned_patterns = []
        self.conversation_db_file = "spitch_conversations.json"
        self.mcp_enabled = False
        self.mcp_client = None
        self.load_learned_data()
        self.init_mcp()
        self.system_prompt = """You are Spitch, a friendly AI assistant. 

IMPORTANT RESPONSE RULES:
- Keep responses SHORT and CONVERSATIONAL (1-3 sentences max)
- NO markdown formatting, tables, or HTML tags
- NO bullet points or numbered lists  
- NO symbols like |, *, #, <br>, etc.
- Use simple, natural language like a human would speak
- Be direct and to the point
- If asked for complex information, summarize briefly in plain text

ACCURACY RULES - CRITICAL:
- NEVER EVER make up or invent movie titles, names, dates, or specific facts
- If you don't know specific information, always say "I don't have that information" or "I don't know"
- Do NOT fabricate movie titles, release dates, actor names, or other specific details
- Do NOT create fake movie names or storylines
- Be completely honest about the limits of your knowledge
- When asked about specific movies or releases, admit if you don't have current information
- It's always better to say "I don't know" than to make something up

Examples of GOOD responses:
- "I don't have information about Telugu movies released in 2025"
- "I don't have current information about specific movie releases"
- "I can help you play music, answer questions, or open applications"
- "Sure! I'll play that song for you on Spotify"
- "I don't have access to real-time movie release information"

Examples of BAD responses (NEVER do these):
- Making up fake movie titles like "Karthikeya 3" or "Super D"
- Inventing release dates or storylines
- Creating fictional actor names or movie details
- Using tables with | symbols
- Long bullet point lists
- HTML tags like <br>
- Fabricating ANY specific facts you don't actually know

Always be honest about what you know and don't know. It's better to say "I don't know" than to make up information."""

    def process_command(self, user_input: str, speak_func=None, system_prompt_override: Optional[str] = None, model: Optional[str] = None, language: str = 'en-US') -> Dict[str, Any]:
        """
        Process user input and return intent and response
        
        Args:
            user_input: The user's command
            speak_func: The function to use for speaking
            system_prompt_override: A temporary system prompt for special cases
            model: The specific AI model to use for this query
            language: The user's preferred language (e.g., 'en-US', 'te-IN', etc.)
        """
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})

            ai_response_text = None
            ai_source = "None"

            # Always use tinyllama unless a different model is explicitly specified
            model_to_use = model if model else OLLAMA_DEFAULT_MODEL

            # FALLBACK CHAIN: Ollama → Google Gemini → OpenRouter
            
            # 1. Try Ollama first (primary AI service - fast and local)
            if OLLAMA_AVAILABLE and spitch_ollama.test_connection():
                try:
                    print("[PROCESSING] Using Ollama for AI processing...")
                    ai_response_text = spitch_ollama.process_query(
                        user_input, 
                        timeout=OLLAMA_TIMEOUT, 
                        system_prompt_override=system_prompt_override,
                        model=model_to_use
                    )
                    ai_source = "Ollama"
                except Exception as ollama_error:
                    print(f"[ERROR] Ollama error: {ollama_error}")

            # 2. Try Google Gemini if Ollama failed (free tier)
            if not ai_response_text and GEMINI_AVAILABLE:
                try:
                    print("[PROCESSING] Using Google Gemini for AI processing...")
                    ai_response_text = spitch_gemini.process_query(
                        user_input,
                        system_prompt=system_prompt_override or self.system_prompt,
                        timeout=10
                    )
                    if ai_response_text:
                        ai_source = "Google Gemini"
                except Exception as gemini_error:
                    print(f"[ERROR] Google Gemini error: {gemini_error}")

            # 3. Fallback to OpenRouter if both Ollama and Gemini failed
            if not ai_response_text and API_AVAILABLE and client:
                try:
                    print(f"[PROCESSING] Using {MODEL_NAME} for AI processing...")
                    
                    # Prepare messages for the API with language, personalized, and MCP context
                    language_context = self._get_language_context(language)
                    personalized_context = self.get_personalized_context(user_input)
                    mcp_context = self.get_mcp_context()
                    system_prompt_with_context = (system_prompt_override or self.system_prompt) + language_context + personalized_context + mcp_context
                    
                    messages = [
                        {"role": "system", "content": system_prompt_with_context}
                    ]
                    
                    # Add recent conversation history (last 5 exchanges)
                    recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
                    messages.extend(recent_history)
                    
                    # Add current user input
                    messages.append({"role": "user", "content": user_input})
                    
                    # Make API call
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    
                    ai_response_text = response.choices[0].message.content
                    ai_source = "OpenRouter" if BASE_URL else "OpenAI"
                    print(f"[OK] Got response from {ai_source}")
                    print(f"[INFO] Raw AI response: {ai_response_text[:200]}..." if ai_response_text else "[INFO] Empty response received")
                    
                except Exception as api_error:
                    print(f"[ERROR] API error: {api_error}")
                    ai_response_text = None


            # If all AI services fail, use a simple fallback
            if not ai_response_text:
                print("[ERROR] All AI services failed - using fallback response")
                return {
                    "intent": {"type": "fallback", "action_required": False},
                    "response": "I'm sorry, I'm having trouble processing that right now. Could you try again?",
                    "ai_source": "Error"
                }
            
            # --- New Intent Processing Logic ---
            try:
                # First check if the response looks like JSON
                if ai_response_text.strip().startswith('{') and ai_response_text.strip().endswith('}'):
                    # Try to parse as JSON
                    intent = json.loads(ai_response_text)
                    # If parsing succeeds, we have a command intent.
                    # Generate a user-friendly response based on the intent.
                    response_for_user = self._create_confirmation_response(intent)
                    print(f"[OK] Parsed AI intent (JSON): {intent}")
                else:
                    # It's clearly a conversational response
                    raise json.JSONDecodeError("Not JSON format", ai_response_text, 0)

            except json.JSONDecodeError:
                # If parsing fails, it's a conversational response.
                intent = {"type": "conversation", "action_required": False}
                response_for_user = self._clean_response(ai_response_text.strip())
                print(f"[OK] Received conversational AI response: {response_for_user}")

            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response_for_user})

            # Learn from this interaction
            self.learn_from_interaction(user_input, response_for_user)

            return {
                "intent": intent,
                "response": response_for_user,
                "ai_source": ai_source
            }

        except Exception as e:
            print(f"[ERROR] AI processing error: {e}")
            return {
                "intent": {"type": "fallback", "action_required": False},
                "response": "I'm sorry, an unexpected error occurred. Please try again.",
                "ai_source": "Error"
            }

    def _clean_response(self, response: str) -> str:
        """Clean up AI response by removing markdown, HTML, and complex formatting"""
        import re
        
        # Only clean if the response contains problematic formatting
        if not any(char in response for char in ['|', '<', '>', '**', '##', '---']):
            # Response is already clean, just normalize whitespace
            return re.sub(r'\s+', ' ', response.strip())
        
        # Remove HTML tags
        response = re.sub(r'<[^>]+>', '', response)
        
        # Remove markdown table formatting (only if it looks like a table)
        if '|' in response and response.count('|') > 2:
            response = re.sub(r'\|[^|]*\|', '', response)
            response = re.sub(r'\|[-\s]*\|', '', response)
        
        # Remove markdown formatting
        response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)  # Bold
        response = re.sub(r'\*(.*?)\*', r'\1', response)      # Italic
        response = re.sub(r'#{1,6}\s*', '', response)         # Headers
        
        # Only remove bullet points if there are multiple lines with them
        if response.count('\n') > 1 and ('- ' in response or '* ' in response or '+ ' in response):
            response = re.sub(r'^\s*[-*+]\s*', '', response, flags=re.MULTILINE)
        
        # Only remove numbered lists if there are multiple lines with them
        if response.count('\n') > 1 and re.search(r'^\s*\d+\.', response, re.MULTILINE):
            response = re.sub(r'^\s*\d+\.\s*', '', response, flags=re.MULTILINE)
        
        # Remove excessive line breaks and clean up
        response = re.sub(r'\n{3,}', '\n\n', response)
        response = re.sub(r'^\s+|\s+$', '', response)
        
        # Only remove table-like structures if they're clearly tables
        if '|' in response or '---' in response:
            lines = response.split('\n')
            cleaned_lines = []
            for line in lines:
                # Skip lines that are clearly table separators or headers
                if not (line.strip().startswith('|') and line.strip().endswith('|')) and '---' not in line and not line.strip().startswith('Category'):
                    cleaned_lines.append(line.strip())
            
            # Only join with spaces if we actually removed table content
            if len(cleaned_lines) < len(lines):
                response = ' '.join(cleaned_lines)
            else:
                response = '\n'.join(cleaned_lines)
        
        # Final cleanup
        response = re.sub(r'\s+', ' ', response)  # Multiple spaces to single space
        
        return response.strip()

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

    def _get_language_context(self, language: str) -> str:
        """Get language-specific context for AI responses"""
        language_instructions = {
            'en-US': "\n\nRespond in English.",
            'te-IN': "\n\nRespond in Telugu (తెలుగు). Use Telugu script and be culturally appropriate for Telugu speakers.",
            'kn-IN': "\n\nRespond in Kannada (ಕನ್ನಡ). Use Kannada script and be culturally appropriate for Kannada speakers.",
            'ml-IN': "\n\nRespond in Malayalam (മലയാളം). Use Malayalam script and be culturally appropriate for Malayalam speakers.",
            'hi-IN': "\n\nRespond in Hindi (हिन्दी). Use Devanagari script and be culturally appropriate for Hindi speakers."
        }
        
        return language_instructions.get(language, language_instructions['en-US'])

    def load_learned_data(self):
        """Load previously learned conversation patterns and preferences"""
        try:
            import json
            import os
            if os.path.exists(self.conversation_db_file):
                with open(self.conversation_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_preferences = data.get('preferences', {})
                    self.learned_patterns = data.get('patterns', [])
                    print(f"[OK] Loaded {len(self.learned_patterns)} learned conversation patterns")
        except Exception as e:
            print(f"[WARNING] Could not load learned data: {e}")
            self.user_preferences = {}
            self.learned_patterns = []

    def save_learned_data(self):
        """Save conversation patterns and preferences for future learning"""
        try:
            import json
            data = {
                'preferences': self.user_preferences,
                'patterns': self.learned_patterns,
                'last_updated': str(datetime.datetime.now())
            }
            with open(self.conversation_db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARNING] Could not save learned data: {e}")

    def learn_from_interaction(self, user_input: str, ai_response: str, user_feedback: str = None):
        """Learn from user interactions to improve future responses"""
        try:
            # Extract patterns from successful interactions
            pattern = {
                'user_query': user_input.lower().strip(),
                'response': ai_response,
                'timestamp': str(datetime.datetime.now()),
                'feedback': user_feedback
            }
            
            # Store successful patterns (limit to last 100 to avoid huge files)
            self.learned_patterns.append(pattern)
            if len(self.learned_patterns) > 100:
                self.learned_patterns = self.learned_patterns[-100:]
            
            # Learn user preferences
            self._extract_preferences(user_input, ai_response)
            
            # Save learned data
            self.save_learned_data()
            
        except Exception as e:
            print(f"[WARNING] Learning error: {e}")

    def _extract_preferences(self, user_input: str, ai_response: str):
        """Extract user preferences from interactions"""
        user_lower = user_input.lower()
        
        # Learn language preferences
        if any(word in user_lower for word in ['telugu', 'tamil', 'hindi', 'kannada', 'malayalam']):
            lang_mentioned = None
            if 'telugu' in user_lower:
                lang_mentioned = 'telugu'
            elif 'tamil' in user_lower:
                lang_mentioned = 'tamil'
            elif 'hindi' in user_lower:
                lang_mentioned = 'hindi'
            elif 'kannada' in user_lower:
                lang_mentioned = 'kannada'
            elif 'malayalam' in user_lower:
                lang_mentioned = 'malayalam'
            
            if lang_mentioned:
                self.user_preferences['preferred_language'] = lang_mentioned
        
        # Learn topic interests
        topics = []
        if any(word in user_lower for word in ['movie', 'film', 'cinema']):
            topics.append('movies')
        if any(word in user_lower for word in ['music', 'song', 'spotify']):
            topics.append('music')
        if any(word in user_lower for word in ['weather', 'temperature']):
            topics.append('weather')
        if any(word in user_lower for word in ['time', 'date', 'calendar']):
            topics.append('time')
        
        if topics:
            if 'interests' not in self.user_preferences:
                self.user_preferences['interests'] = {}
            for topic in topics:
                self.user_preferences['interests'][topic] = self.user_preferences['interests'].get(topic, 0) + 1

    def get_personalized_context(self, user_input: str) -> str:
        """Get personalized context based on learned patterns"""
        context = ""
        
        # Add user preferences to context
        if self.user_preferences:
            if 'preferred_language' in self.user_preferences:
                lang = self.user_preferences['preferred_language']
                context += f"\nUser shows interest in {lang} content. "
            
            if 'interests' in self.user_preferences:
                top_interests = sorted(self.user_preferences['interests'].items(), 
                                     key=lambda x: x[1], reverse=True)[:3]
                if top_interests:
                    interests_str = ", ".join([interest[0] for interest in top_interests])
                    context += f"User frequently asks about: {interests_str}. "
        
        # Look for similar past interactions
        user_lower = user_input.lower().strip()
        similar_patterns = []
        
        for pattern in self.learned_patterns[-20:]:  # Check last 20 patterns
            if self._is_similar_query(user_lower, pattern['user_query']):
                similar_patterns.append(pattern)
        
        if similar_patterns:
            context += f"\nBased on previous similar questions, user expects concise, helpful responses. "
        
        return context

    def _is_similar_query(self, query1: str, query2: str) -> bool:
        """Check if two queries are similar"""
        # Simple similarity check based on common words
        words1 = set(query1.split())
        words2 = set(query2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        common_words = words1.intersection(words2)
        similarity = len(common_words) / max(len(words1), len(words2))
        
        return similarity > 0.3  # 30% similarity threshold

    def init_mcp(self):
        """Initialize MCP client for enhanced capabilities"""
        try:
            from engine.mcp_client import mcp_client
            import asyncio
            
            self.mcp_client = mcp_client
            
            # Try to connect to MCP server
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.mcp_client.list_tools())
                self.mcp_enabled = True
                print("[OK] MCP client initialized and connected")
            except Exception as conn_error:
                print(f"[WARNING] MCP client created but not connected: {conn_error}")
                self.mcp_enabled = True  # Still enable for tool descriptions
                
        except Exception as e:
            print(f"[WARNING] MCP not available: {e}")
            self.mcp_enabled = False
            self.mcp_client = None

    def get_mcp_context(self) -> str:
        """Get MCP tools context for AI"""
        if self.mcp_enabled and self.mcp_client:
            tools_desc = self.mcp_client.get_tools_description()
            if tools_desc:
                return tools_desc + "\n\nYou can use these MCP tools to provide real-time information and perform actions."
        return ""
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        """Call an MCP tool and return the result"""
        if self.mcp_enabled and self.mcp_client:
            try:
                result = await self.mcp_client.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                print(f"[ERROR] MCP tool call failed: {e}")
                return f"Error calling tool: {str(e)}"
        return "MCP not available"

    def get_quick_response(self, user_input: str) -> str:
        """Get a quick response for simple queries without AI processing"""
        import re
        user_input_lower = user_input.lower().strip()
        
        # Use word boundaries to match whole words only
        def has_whole_word(text, words):
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    return True
            return False
        
        # Quick responses for common greetings (whole words only)
        if has_whole_word(user_input_lower, ['hello', 'hi', 'hey']) or any(phrase in user_input_lower for phrase in ['good morning', 'good evening']):
            return "Hello! How can I help you today?"
        
        elif has_whole_word(user_input_lower, ['bye', 'goodbye']) or 'see you' in user_input_lower:
            return "Goodbye! Have a great day!"
        
        elif any(phrase in user_input_lower for phrase in ['thanks', 'thank you']):
            return "You're welcome! Is there anything else I can help you with?"
        
        elif any(phrase in user_input_lower for phrase in ['how are you', 'how do you do']):
            return "I'm doing well, thank you for asking! How can I assist you?"
        
        elif 'what is your name' in user_input_lower or 'who are you' in user_input_lower:
            return "I'm Spitch, your AI assistant! I'm here to help you with various tasks and answer your questions."
        
        elif 'what can you do' in user_input_lower or 'help me' in user_input_lower:
            return "I can help you with many things! I can answer questions, tell jokes, provide information, help with calculations, and much more. Just ask me anything!"
        
        elif user_input_lower in ['test', 'testing', 'hello world']:
            return "Test successful! I'm working properly and ready to help you."
        
        return None  # No quick response available

# Create global instance
spitch_ai = SpitchAI() 