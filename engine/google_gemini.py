"""
Google Gemini Integration for Spitch AI Assistant
Provides access to Google's Gemini models as a fallback AI service
"""

import requests
import json
from typing import Optional, Dict, Any

class GoogleGemini:
    def __init__(self):
        self.api_key = None
        self.model = None
        self.base_url = None
        self.available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Gemini configuration"""
        try:
            from config import GOOGLE_API_KEY, GOOGLE_GEMINI_MODEL, GOOGLE_API_BASE_URL
            
            if GOOGLE_API_KEY and GOOGLE_API_KEY != 'your-google-api-key-here':
                self.api_key = GOOGLE_API_KEY
                self.model = GOOGLE_GEMINI_MODEL
                self.base_url = GOOGLE_API_BASE_URL
                self.available = True
                print(f"[OK] Google Gemini configured with model: {self.model}")
            else:
                print("[WARNING] Google Gemini API key not configured")
                
        except ImportError:
            print("[WARNING] Google Gemini configuration not found")
    
    def test_connection(self) -> bool:
        """Test if Google Gemini API is accessible"""
        if not self.available:
            return False
        
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"[WARNING] Google Gemini connection test failed: {e}")
            return False
    
    def process_query(self, query: str, system_prompt: Optional[str] = None, timeout: int = 10) -> Optional[str]:
        """
        Process a query using Google Gemini
        
        Args:
            query: User's question or command
            system_prompt: System instructions (will be prepended to query)
            timeout: Request timeout in seconds
            
        Returns:
            AI response text or None if failed
        """
        if not self.available:
            return None
        
        try:
            # Construct the prompt
            full_prompt = query
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {query}\n\nAssistant:"
            
            # Prepare the API request
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            # Make the request
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                return text.strip() if text else None
            
            elif response.status_code == 429:
                # Rate limit exceeded
                print("[WARNING] Google Gemini rate limit exceeded")
                return None
            
            else:
                print(f"[WARNING] Google Gemini API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("[WARNING] Google Gemini request timeout")
            return None
        except Exception as e:
            print(f"[WARNING] Google Gemini error: {e}")
            return None

    def process_vision_query(self, query: str, image_bytes: bytes, timeout: int = 15) -> Optional[str]:
        """
        Process a vision query (text + image) using Google Gemini
        """
        if not self.available:
            return None
            
        try:
            import base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Use 'gemini-1.5-flash' or 'gemini-pro-vision' if available, fallback to current model
            vision_model = self.model
            if 'flash' not in vision_model and 'vision' not in vision_model:
                vision_model = 'gemini-1.5-flash' # Default to flash for vision
            
            url = f"{self.base_url}/models/{vision_model}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            
            data = {
                "contents": [{
                    "parts": [
                        {"text": query},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_b64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 800
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                return text.strip() if text else None
            else:
                print(f"[WARNING] Gemini Vision API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[WARNING] Gemini Vision error: {e}")
            return None

    
    def get_available_models(self) -> list:
        """Get list of available Gemini models"""
        if not self.available:
            return []
        
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                gemini_models = [
                    m.get('name') for m in models 
                    if 'gemini' in m.get('name', '').lower() 
                    and 'generateContent' in m.get('supportedGenerationMethods', [])
                ]
                return gemini_models
            return []
        except Exception as e:
            print(f"[WARNING] Error fetching models: {e}")
            return []

# Global instance
spitch_gemini = GoogleGemini()
