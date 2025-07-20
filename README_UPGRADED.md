# 🎵 Sophia AI Assistant - AI-Powered Personal Assistant

**Sophia is now powered by ChatGPT and Spotify APIs, making it as intelligent as ChatGPT and as capable as Siri for music control!**

## ✨ New Features

### 🤖 **ChatGPT Integration**
- **Natural Language Understanding**: Sophia now understands natural language like ChatGPT
- **Conversational AI**: Have natural conversations, ask questions, get intelligent responses
- **Context Awareness**: Remembers conversation history and provides contextual responses
- **General Knowledge**: Answer questions about any topic, just like ChatGPT

### 🎵 **True Siri-like Spotify Control**
- **Spotify Web API Integration**: Direct control of your Spotify desktop app
- **Play Any Song**: Say "Play [song name] from Spotify" and it actually plays!
- **Device Control**: Automatically detects and uses your desktop app
- **No UI Automation**: Uses official Spotify API for reliable control

### 🔧 **Smart Command Processing**
- **Intent Recognition**: Automatically detects what you want to do
- **Multiple Platforms**: Works with voice commands and text input
- **Fallback Systems**: If one method fails, tries alternatives
- **Error Handling**: Graceful error handling with helpful responses

## 🚀 Quick Start

### 1. **Setup API Keys**
```bash
# Run the setup script
py -3.12 setup_sophia.py
```

This will guide you through:
- Setting up Spotify Developer App
- Getting OpenAI API key
- Testing the integration

### 2. **Start Sophia**
```bash
py -3.12 main.py
```

### 3. **Try These Commands**

#### 🎵 **Music Commands**
- "Play despacito from Spotify"
- "Play shape of you on Spotify"
- "Play cornfield chase from spotify app"
- "Play music by Ed Sheeran"

#### 🤖 **Conversational Commands**
- "What's the weather like?"
- "Tell me a joke"
- "What's the capital of France?"
- "How do I make pasta?"
- "Explain quantum physics"

#### 🔧 **System Commands**
- "Open notepad"
- "Take a screenshot"
- "What time is it?"
- "Search for Python tutorials"
- "Open file explorer"

## 📋 Requirements

### **Python Dependencies**
```bash
py -3.12 -m pip install spotipy openai requests pyttsx3 speechrecognition eel pyautogui playsound
```

### **API Keys Required**
1. **Spotify API** (Free)
   - Go to: https://developer.spotify.com/dashboard
   - Create an app and get Client ID & Secret

2. **OpenAI API** (Free trial available)
   - Go to: https://platform.openai.com/api-keys
   - Create an API key

## 🔧 Configuration

Edit `config.py` to customize:
```python
# Spotify API Configuration
SPOTIPY_CLIENT_ID = "your_spotify_client_id"
SPOTIPY_CLIENT_SECRET = "your_spotify_client_secret"

# OpenAI API Configuration
OPENAI_API_KEY = "your_openai_api_key"

# Assistant Configuration
ASSISTANT_NAME = "Sophia"
VOICE_RATE = 170
```

## 🎯 How It Works

### **AI-Powered Command Processing**
1. **Input**: Voice or text command
2. **AI Analysis**: ChatGPT analyzes intent and context
3. **Intent Extraction**: Determines what action to take
4. **Action Execution**: Performs the requested action
5. **Response**: Provides intelligent, contextual response

### **Spotify Integration**
1. **Song Request**: "Play despacito from Spotify"
2. **API Search**: Searches Spotify for the song
3. **Device Detection**: Finds your active Spotify device
4. **Direct Play**: Uses Spotify API to start playback
5. **Confirmation**: Confirms what's playing

## 🎵 Spotify Setup

### **Step 1: Create Spotify App**
1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create an App"
4. Name: `SophiaAI`
5. Description: `Personal AI Assistant`

### **Step 2: Configure App**
1. Click on your app
2. Go to "Edit Settings"
3. Add Redirect URI: `http://localhost:8888/callback`
4. Save

### **Step 3: Get Credentials**
1. Copy your **Client ID**
2. Copy your **Client Secret**
3. Add them to `config.py`

## 🤖 OpenAI Setup

### **Step 1: Get API Key**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key

### **Step 2: Configure**
1. Add the key to `config.py`
2. The free tier includes $5 credit (enough for testing)

## 🎮 Usage Examples

### **Voice Commands**
```
"Hey Sophia, play despacito from Spotify"
"Play shape of you on spotify app"
"What's the weather like today?"
"Open notepad for me"
"Tell me a joke"
"What's 15 times 23?"
"Take a screenshot"
"Search for Python tutorials"
```

### **Text Commands**
- Use the text input box in the web interface
- Type any command and press Enter
- Same functionality as voice commands

## 🔧 Troubleshooting

### **Spotify Issues**
- **"No active devices"**: Make sure Spotify is open on your computer
- **"Authentication failed"**: Check your Client ID and Secret
- **"Song not found"**: Try a different song name or artist

### **OpenAI Issues**
- **"API key invalid"**: Check your OpenAI API key
- **"Rate limit exceeded"**: Wait a moment and try again
- **"No response"**: Check your internet connection

### **General Issues**
- **Voice not working**: Check microphone permissions
- **Text input not working**: Refresh the web page
- **App not starting**: Check Python version (3.12 recommended)

## 🎯 Advanced Features

### **Conversation Memory**
- Sophia remembers your conversation history
- Provides contextual responses
- Learns from your preferences

### **Multi-Platform Support**
- Works on Windows, macOS, Linux
- Supports multiple Spotify devices
- Cross-platform voice recognition

### **Extensible Architecture**
- Easy to add new commands
- Modular design for easy customization
- Plugin system for additional features

## 🚀 Future Enhancements

- **Weather API Integration**: Real-time weather data
- **Calendar Integration**: Schedule management
- **Email Integration**: Send and read emails
- **Smart Home Control**: IoT device integration
- **Language Support**: Multiple languages
- **Voice Customization**: Different voices and accents

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify your API keys are correct
3. Ensure all dependencies are installed
4. Check that Spotify is open and running

## 🎉 Enjoy Your AI Assistant!

Sophia now combines the intelligence of ChatGPT with the functionality of Siri and Google Assistant. Have fun exploring all the possibilities!

---

**Made with ❤️ for AI enthusiasts** 