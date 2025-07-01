# 🗣️ Spitch AI Assistant - Your Local AI-Powered Desktop Assistant

**Spitch is a modern, extensible desktop AI assistant powered by local LLMs (Ollama) and advanced APIs. It can answer questions, control your desktop, play music, browse the web, and more—all via voice or text.**

---

## ✨ Features

- **Conversational AI**: Natural language chat, context awareness, and general knowledge (Ollama LLMs, OpenAI fallback)
- **Voice & Text Input**: Activate by voice or type commands in the web UI
- **App & Web Control**: Open desktop apps, launch websites, search the web
- **Spotify Integration**: Play any song, artist, or playlist using the official Spotify API
- **YouTube Control**: Search and play YouTube videos
- **System Utilities**: Take screenshots, tell time/date, control system apps
- **Extensible**: Modular Python architecture for easy feature addition
- **Configurable**: All settings in `config.py` (API keys, assistant name, toggles)

---

## 🚀 Quick Start

### 1. **Clone the Repository**
```bash
git clone https://github.com/sujithputta02/spitch-ai-assistant.git
cd spitch-ai-assistant
```

### 2. **Install Dependencies**
```bash
python -m pip install -r requirements.txt
```

### 3. **Configure API Keys**
Edit `config.py` and set:
- **Ollama**: (Recommended) Install Ollama from https://ollama.ai/ and pull a model (e.g., `ollama pull phi3`)
- **OpenAI API Key**: (Optional fallback)
- **Spotify API Keys**: [Get from Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- **Weather/News API Keys**: (Optional)

### 4. **Run the Assistant**
```bash
python main.py
```
This will launch the web UI (Eel) and start listening for commands.

---

## 🛠️ Configuration

All settings are in `config.py`:
- **Assistant Name**: `ASSISTANT_NAME = "Spitch"`
- **Ollama Model/URL**: `OLLAMA_DEFAULT_MODEL`, `OLLAMA_BASE_URL`
- **OpenAI API Key**: `OPENAI_API_KEY`
- **Spotify Credentials**: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`
- **Feature Toggles**: Enable/disable voice, wake word, etc.
- **API Keys**: Weather, News, etc.

---

## 🎤 Usage

- **Voice Activation**: Click the mic button or say "Spitch" (if wake word enabled)
- **Text Input**: Type in the web UI and press Enter
- **Keyboard Shortcut**: (If configured)

### Example Commands
- "Open Notepad"
- "Play Shape of You from Spotify"
- "Search for Python tutorials"
- "What's the weather like?"
- "Take a screenshot"
- "Tell me a joke"

## 🗣️ Prompt Examples

Spitch understands natural language! Here are some example prompts you can try (but feel free to use your own phrasing):

### Basic Commands
- "What time is it?"
- "What's the date today?"
- "Open notepad"
- "Launch Chrome"
- "Search for the latest AI news"
- "Google how to make a perfect omelette"
- "What is 25 times 8?"
- "Take a screenshot"
- "What are my computer specs?"
- "Set my location to New York"
- "What's the weather like?"
- "What's the 5-day forecast?"
- "Tell me a joke"
- "What can you do?"

### Music & Spotify
- "Play Cornfield Chase on Spotify"
- "Play music similar to Coldplay on Spotify"
- "Create a playlist called Road Trip on Spotify"
- "Play my Discover Weekly playlist"
- "Pause the song"
- "Resume the music"
- "I'm feeling sad — play something comforting on Spotify"
- "Find trending songs on Spotify"
- "What are the top 10 songs on Spotify right now?"
- "Recommend a playlist for working out on Spotify"
- "Add this song to my Chill Vibes playlist on Spotify"
- "Play something relaxing on Spotify"
- "I need a boost — play motivational tracks on Spotify"
- "Find a true crime podcast with high ratings on Spotify"
- "Play the latest episode of The Daily on Spotify"
- "What's my most played song this week on Spotify?"
- "Who are my most listened-to artists on Spotify?"

### YouTube & Video
- "Play a tutorial on Python on YouTube"
- "Pause YouTube"
- "Find me the latest videos about AI in healthcare"
- "Show me beginner tutorials on photo editing"
- "Give me video title ideas for a travel channel"
- "Write a YouTube video script intro for a tech review"
- "Suggest thumbnail ideas and colors for a gaming video"
- "Create a YouTube Shorts concept under 60 seconds about productivity"
- "Write an engaging video description for a cooking tutorial"
- "What are some YouTube SEO strategies to grow my channel?"
- "How do I optimize my videos for more watch time?"

### Advanced & Community
- "What questions should I ask my audience in a fitness video?"
- "Suggest a call to action for viewers"
- "What community post should I create to boost engagement?"
- "Give me ideas for polls for my YouTube Community tab"
- "What are the YouTube monetization requirements?"
- "Suggest passive income strategies for a small YouTube creator"
- "How do I get brand sponsorships for my channel?"

---

## 🧩 Architecture

- **main.py**: Launches the Eel web UI and manages voice/text input
- **app.py**: Flask API endpoints for advanced integrations
- **engine/**: Core logic (features, AI, Spotify, commands, etc.)
- **www/**: Web UI (HTML, CSS, JS)
- **config.py**: All configuration

---

## 🧑‍💻 Extending Spitch

- Add new features in `engine/features.py` or as new modules
- Add new web UI elements in `www/`
- Use the modular command system for easy intent/action mapping

---

## 🩹 Troubleshooting

- **Ollama not responding**: Ensure Ollama is running and the model is pulled (`ollama pull phi3`)
- **Spotify issues**: Make sure Spotify is open and credentials are correct
- **Voice not working**: Check microphone permissions
- **API errors**: Double-check your API keys in `config.py`
- **App not starting**: Use Python 3.12+, check dependencies

---

## 🤝 Contributing

Pull requests and issues are welcome! Help improve Spitch by adding features, fixing bugs, or enhancing documentation.

---

## 📢 Feedback

Open an issue or leave feedback on the project repository. Your suggestions help make Spitch better!
