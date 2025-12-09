# Sophia AI Assistant Configuration

# Ollama Configuration (PRIMARY AI SERVICE)
# Make sure Ollama is installed and running: https://ollama.ai/
# Install the phi3 model: ollama pull phi3
OLLAMA_DEFAULT_MODEL = 'tinyllama'  # Primary AI model
OLLAMA_BASE_URL = 'http://localhost:11434'

# OpenAI API Configuration (OPTIONAL FALLBACK)
# Get your API key from: https://platform.openai.com/account/api-keys
# Replace 'your-openai-api-key-here' with your actual API key
# This is only used as a fallback if Ollama is not available
OPENAI_API_KEY = 'your-openai-api-key-here'

# OpenRouter Configuration (for alternative models)
OPENROUTER_API_KEY = 'your-openrouter-api-key-here'
OPENROUTER_MODEL = 'openai/gpt-oss-20b:free'
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'

# Google Gemini Configuration (FREE TIER - use with caution due to rate limits)
GOOGLE_API_KEY = 'your-google-api-key-here'
GOOGLE_GEMINI_MODEL = 'gemini-2.5-flash'  # Fast and free tier friendly
GOOGLE_API_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

# Alternative: Set your API key as an environment variable
# In Windows Command Prompt: set OPENAI_API_KEY=your-actual-key-here
# In PowerShell: $env:OPENAI_API_KEY="your-actual-key-here"

# Assistant Configuration
ASSISTANT_NAME = "Spitch"

# Voice Configuration
VOICE_RATE = 170  # Speech rate (words per minute)
VOICE_VOLUME = 1.0  # Voice volume (0.0 to 1.0)

# Web Interface Configuration
WEB_PORT = 8000
WEB_HOST = 'localhost'

# Database Configuration
DATABASE_PATH = "spitch.db"

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Feature Toggles
ENABLE_CONTINUOUS_LISTENING = True
ENABLE_WAKE_WORD = True
ENABLE_VOICE_COMMANDS = True
ENABLE_TEXT_COMMANDS = True

# Timeout Settings (in seconds) - Optimized for Ollama
OLLAMA_TIMEOUT = 15  # Primary AI service timeout
OPENAI_TIMEOUT = 10  # Fallback timeout
VOICE_RECOGNITION_TIMEOUT = 10

# Spotify Configuration (if you have Spotify API credentials)
# Get your credentials from: https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = 'your-spotify-client-id-here'
SPOTIFY_CLIENT_SECRET = 'your-spotify-client-secret-here'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Weather API Configuration (optional)
# Get your API key from: https://openweathermap.org/api
WEATHER_API_KEY = 'your-weather-api-key-here'

# News API Configuration (optional)
# Get your API key from: https://newsapi.org/
NEWS_API_KEY = 'your-news-api-key-here'

# MySQL configuration removed - using SQLite database instead
