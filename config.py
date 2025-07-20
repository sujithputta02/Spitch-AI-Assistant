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
SPOTIFY_CLIENT_ID = '65b0dda2962c4b8db17ddc41c9825149'
SPOTIFY_CLIENT_SECRET = 'ad5e1281cfd24401b668b67a4ac4231a'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Weather API Configuration (optional)
# Get your API key from: https://openweathermap.org/api
WEATHER_API_KEY = 'your-weather-api-key-here'

# News API Configuration (optional)
# Get your API key from: https://newsapi.org/
NEWS_API_KEY = 'your-news-api-key-here'

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Sujith@20$'
MYSQL_DATABASE = 'spitch_ai' 