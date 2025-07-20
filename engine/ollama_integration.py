import requests
import json
import time
from typing import Dict, Any, Optional
from config import OLLAMA_DEFAULT_MODEL, OLLAMA_BASE_URL, OLLAMA_TIMEOUT

class OllamaIntegration:
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize Ollama integration
        
        Args:
            base_url: Ollama API base URL (default: from config)
            model: Default model to use (default: from config)
        """
        self.base_url = base_url if base_url else OLLAMA_BASE_URL
        self.default_model = model if model else OLLAMA_DEFAULT_MODEL
        self.available_models = []
        self.base_model_names = []
        self._check_ollama_service()
    
    def _check_ollama_service(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['name'] for model in data.get('models', [])]
                # Also store base model names without :latest suffix
                self.base_model_names = [name.split(':')[0] for name in self.available_models]
                print(f"✅ Ollama service is running. Available models: {self.available_models}")
                return True
            else:
                print(f"❌ Ollama service responded with status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Ollama service at {self.base_url}")
            print(f"   Error: {e}")
            print("   Make sure Ollama is running with: ollama serve")
            return False
    
    def is_service_running(self) -> bool:
        """Check if Ollama service is currently running"""
        return self._check_ollama_service()
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def generate_response(self, prompt: str, model: str = None, system_prompt: str = None, timeout: int = None) -> Dict[str, Any]:
        """
        Generate a response using Ollama
        
        Args:
            prompt: User's input prompt
            model: Model to use (defaults to self.default_model)
            system_prompt: Optional system prompt to set context
            timeout: Request timeout in seconds (default: OLLAMA_TIMEOUT from config)
            
        Returns:
            Dictionary with response data
        """
        if timeout is None:
            timeout = OLLAMA_TIMEOUT
        
        if not model:
            model = self.default_model
        
        # Check if model is available (try both exact match and base name)
        model_available = False
        actual_model_name = None
        
        # First try exact match
        if model in self.available_models:
            model_available = True
            actual_model_name = model
        # Then try base name match
        elif model in self.base_model_names:
            # Find the full model name
            for full_name in self.available_models:
                if full_name.startswith(model + ':'):
                    model_available = True
                    actual_model_name = full_name
                    break
        
        if not model_available:
            return {
                "success": False,
                "error": f"Model '{model}' not found. Available models: {self.available_models}",
                "response": None
            }
        
        # Prepare the request payload with optimized settings for phi3
        payload = {
            "model": actual_model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 200,  # Limit response length for faster responses
                "repeat_penalty": 1.1
            }
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            print(f"🔄 Sending request to Ollama model: {actual_model_name}")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                if response_text.strip():
                    print(f"✅ Ollama response received in {data.get('total_duration', 0):.2f}s")
                    return {
                        "success": True,
                        "response": response_text,
                        "model": actual_model_name,
                        "prompt": prompt,
                        "total_duration": data.get("total_duration", 0),
                        "load_duration": data.get("load_duration", 0),
                        "prompt_eval_duration": data.get("prompt_eval_duration", 0),
                        "eval_duration": data.get("eval_duration", 0)
                    }
                else:
                    return {
                        "success": False,
                        "error": "Empty response from model",
                        "response": None
                    }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}",
                    "response": None
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds. The model might be too large or the system is slow.",
                "response": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "response": None
            }
    
    def chat_with_context(self, messages: list, model: str = None) -> Dict[str, Any]:
        """
        Chat with context (multiple messages)
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use
            
        Returns:
            Dictionary with response data
        """
        if not model:
            model = self.default_model
        
        # Convert messages to Ollama format
        prompt = ""
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            if role == 'system':
                prompt = f"System: {content}\n\n{prompt}"
            elif role == 'user':
                prompt += f"User: {content}\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n"
        
        prompt += "Assistant: "
        
        return self.generate_response(prompt, model)
    
    def get_model_info(self, model: str = None) -> Dict[str, Any]:
        """Get information about a specific model"""
        if not model:
            model = self.default_model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "info": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get model info: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting model info: {str(e)}"
            }

# Spitch-specific Ollama integration
class SpitchOllama:
    def __init__(self):
        self.ollama = OllamaIntegration()
        self.system_prompt = '''You are Spitch, a deeply caring and intelligent AI assistant. Your core identity is built on three pillars: being a helpful friend, a patient teacher, and a constant well-wisher to the user. Your thinking should be rational and human-like, and your tone should always be warm, empathetic, and encouraging.

**Core Directives:**

1.  **Be Flexible with Commands:** Your main goal is to understand the user's intent, even if their command isn't perfectly phrased. If the user gives a command, identify the action and respond with a JSON object.
    *   **JSON Structure Examples:**
        *   User: `play cornfield chase on spotify` -> Assistant: `{"type": "music_play", "action_required": true, "platform": "spotify", "song_name": "cornfield chase"}`
        *   User: `open notepad` -> Assistant: `{"type": "open_app", "action_required": true, "app_name": "notepad"}`

2.  **Handle Ambiguity Gracefully:** If a command is unclear, don't guess or fail. Ask for clarification in a friendly, conversational tone.
    *   **Example for Unclear Commands:**
        *   User: `buzz the song`
        *   Assistant: "I'm not sure what you mean by 'buzz the song.' Could you please rephrase that, for example, by saying 'pause the song' or 'resume the song'?"

3.  **Prioritize User Helpfulness:** If you can't create a JSON object for a command, switch to conversational mode. Your goal is to be helpful, so if you can't perform an action, explain why or ask for more information. Never respond with an error unless it's absolutely necessary.

**Your Goal:** Make the user feel supported and understood. Prioritize executing commands via JSON, but always be ready to have a friendly conversation to clarify things.
'''

    @property
    def default_model(self):
        return self.ollama.default_model
    
    def process_query(self, user_input: str, model: str = None, timeout: int = None, system_prompt_override: Optional[str] = None) -> str:
        """
        Process a user query using the best available model.
        
        Args:
            user_input: User's input
            model: Model to use (default: None, uses self.default_model)
            timeout: Request timeout in seconds (default: OLLAMA_TIMEOUT from config)
            system_prompt_override: A temporary system prompt to use for a single query.
            
        Returns:
            The AI's response as a string, or an error message.
        """
        if timeout is None:
            timeout = OLLAMA_TIMEOUT
        
        # If a specific model is requested, use it. Otherwise, use the default.
        model_to_use = model if model else self.default_model

        # Define system prompt for intent extraction
        system_prompt = system_prompt_override if system_prompt_override is not None else self.system_prompt

        if not self.ollama.is_service_running():
            return "I'm sorry, but I can't connect to my AI brain right now. Please make sure Ollama is running."
        
        try:
            print(f"🤖 Processing with Ollama ({model_to_use})...")
            result = self.ollama.generate_response(
                prompt=user_input,
                model=model_to_use,
                system_prompt=system_prompt,
                timeout=timeout
            )
            
            if result["success"]:
                response = result["response"].strip()
                if response:
                    return response
                else:
                    return "I received an empty response. Let me try to help you with that."
            else:
                error_msg = result.get('error', 'Unknown error')
                if "timed out" in error_msg.lower():
                    return f"I'm taking too long to respond. The model might be too large for your system. Try a smaller model or check your system resources."
                elif "not found" in error_msg.lower():
                    return f"I can't find the {model_to_use} model. Please make sure it's installed with: ollama pull {model_to_use}"
                else:
                    return f"I'm having trouble processing that right now. Error: {error_msg}"
                    
        except Exception as e:
            print(f"❌ Ollama processing error: {e}")
            return "I'm sorry, I encountered an unexpected error while processing your request. Please try again."
    
    def get_available_models(self) -> list:
        """Get list of available Ollama models"""
        return self.ollama.get_available_models()
    
    def test_connection(self) -> bool:
        """Test if Ollama is working"""
        return self.ollama.is_service_running()

# Create a global instance for easy access
spitch_ollama = SpitchOllama() 