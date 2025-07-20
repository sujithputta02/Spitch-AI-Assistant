#!/usr/bin/env python3
"""
Sophia AI Assistant Setup Script
This script helps you configure your API keys and test the integration.
"""

import os
import sys

def setup_config():
    """Setup configuration file with API keys"""
    print("🎵 Sophia AI Assistant Setup")
    print("=" * 50)
    print()
    
    # Check if config.py exists
    if os.path.exists('config.py'):
        print("📁 Configuration file found.")
        response = input("Do you want to update your existing configuration? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    print("\n🔑 Let's set up your API keys:")
    print()
    
    # Spotify API Setup
    print("🎵 Spotify API Setup:")
    print("1. Go to: https://developer.spotify.com/dashboard")
    print("2. Log in with your Spotify account")
    print("3. Click 'Create an App'")
    print("4. Name: SophiaAI, Description: Personal AI Assistant")
    print("5. In your app settings, add Redirect URI: http://localhost:8888/callback")
    print("6. Copy your Client ID and Client Secret")
    print()
    
    spotify_client_id = input("Enter your Spotify Client ID: ").strip()
    spotify_client_secret = input("Enter your Spotify Client Secret: ").strip()
    
    # OpenAI API Setup
    print("\n🤖 OpenAI API Setup:")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Sign up or log in")
    print("3. Create a new API key")
    print("4. Copy your API key")
    print()
    
    openai_api_key = input("Enter your OpenAI API key: ").strip()
    
    # Create config file
    config_content = f'''# Sophia AI Assistant Configuration
# Set your API keys here

# Spotify API Configuration
# Get these from: https://developer.spotify.com/dashboard
SPOTIPY_CLIENT_ID = "{spotify_client_id}"
SPOTIPY_CLIENT_SECRET = "{spotify_client_secret}"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

# OpenAI API Configuration
# Get this from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "{openai_api_key}"

# Assistant Configuration
ASSISTANT_NAME = "Sophia"
ASSISTANT_PERSONALITY = "friendly, helpful, and intelligent"

# Voice Configuration
VOICE_RATE = 170
VOICE_VOLUME = 1.0

# Web Interface Configuration
WEB_PORT = 10000
WEB_HOST = "localhost"
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print("\n✅ Configuration saved to config.py")
    print()

def test_integration():
    """Test the API integrations"""
    print("🧪 Testing API Integrations:")
    print()
    
    try:
        # Test OpenAI
        print("Testing OpenAI API...")
        from engine.ai_assistant import sophia_ai
        result = sophia_ai.process_command("Hello, how are you?")
        print(f"✅ OpenAI API working: {result['response'][:50]}...")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
    
    try:
        # Test Spotify (without actually playing)
        print("\nTesting Spotify API...")
        from engine.spotify_api import sp
        # Just test if we can access the API
        user = sp.current_user()
        print(f"✅ Spotify API working: Connected as {user['display_name']}")
    except Exception as e:
        print(f"❌ Spotify API error: {e}")
        print("   Make sure you've set up your Spotify app correctly and authorized it.")
    
    print("\n🎉 Setup complete!")
    print("\nTo start Sophia:")
    print("1. Make sure Spotify is open on your computer")
    print("2. Run: py -3.12 main.py")
    print("3. Try commands like:")
    print("   - 'Play despacito from spotify'")
    print("   - 'What's the weather like?'")
    print("   - 'Open notepad'")
    print("   - 'Tell me a joke'")

if __name__ == "__main__":
    setup_config()
    test_integration() 