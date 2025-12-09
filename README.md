# 🧠 Spitch AI Assistant (JARVIS-Level)

**The Ultimate Local AI Desktop Assistant with Vision & Multimodal Chat**

Spitch is a cutting-edge, JARVIS-like assistant that controls your computer, understands natural language, and proactively helps you get things done. Powered by local LLMs (Ollama) and advanced Google Gemini models, it features context awareness, persistent memory, intelligent task automation, **computer vision**, and **multimodal chat support**.

---

## ✨ Features Breakdown

### 🗣️ True Natural Language Understanding
*   **Context Aware**: "Open calculator", then "calculate 5+5", then "close **it**". Spitch understands context and pronouns.
*   **Conversational Memory**: Remembers your previous interactions and preferences across sessions.
*   **No "Commands"**: Just talk naturally. "I want to write a python script" instead of "open pattern X".

### 👁️ **NEW: Vision & Multimodal Capabilities**
*   **Image Upload**: Attach images directly in the chat interface using the 📎 paperclip button.
*   **Visual Understanding**: Ask questions about images: "What's in this screenshot?", "Explain this diagram", "What code is shown here?"
*   **Screen Analysis**: "Take a screenshot and tell me what's on my screen" - Spitch can capture and analyze your display.
*   **Powered by Gemini Vision**: Uses Google's Gemini 1.5 Flash for advanced image understanding.

### ⚙️ **NEW: Customizable Settings**
*   **Voice Selection**: Choose from multiple TTS voices (Male/Female/Microsoft voices).
*   **Speed Control**: Adjust how fast Spitch speaks (100-250 WPM).
*   **Default Location**: Set your city for personalized weather and local information.
*   **Persistent Preferences**: All settings are saved and remembered across sessions.

### ⚡ Seamless Task Execution & Browser Control
*   **Browser Integration**: "Open Gemini **in browser**" or "Search for Python tutorials" launches your default browser (Chrome/Edge/Firefox) instantly.
*   **Robust Automation**: 3-stage retry logic ensures commands work even if apps are slow to load.
*   **App Control**: Precise control over desktop applications (Notepad, Calculator, Spotify, etc.).
*   **Window Management**: Handles minimized windows, multi-monitor setups, and focus stealing.

### 🔮 Proactive Assistance
*   **Smart Suggestions**: Suggests actions based on the time of day (e.g., "Good morning, open your email?").
*   **Pattern Learning**: Learns your habits (e.g., "You usually open Spotify at 2 PM, shall I do that?").
*   **System Monitoring**: Real-time health checks on CPU, memory, and disk usage.

### 📂 File Intelligence
*   **Smart Organization**: "Organize my downloads" auto-sorts files into Documents, Images, Code, etc.
*   **Content Search**: "Search for that report I worked on last week".
*   **Duplicate Detection**: Finds and helps clean up duplicate files.
*   **Recent Access**: Tracks your workflow to surface relevant files.

### 💻 Developer Tools
*   **Git Integration**: "Check git status", "Commit changes with message 'update'", "Push to remote".
*   **Shell Integration**: Run terminal commands directly via voice or text.
*   **Code Management**: Intelligent project root detection and management.
*   **Safety Sandbox**: Validates potentially dangerous commands before execution.

### 🧩 **NEW: Dynamic Skill Registry**
*   **Extensible Architecture**: Easily add new skills without modifying core code.
*   **Auto-Discovery**: New skills are automatically recognized by the AI.
*   **Centralized Management**: All capabilities managed through a unified registry system.

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/sujithputta02/spitch-ai-assistant.git
cd spitch-ai-assistant
pip install -r requirements.txt
```

### 2. Configuration
Edit `config.py` with your preferences:
*   **AI Backend**: Set `OLLAMA_BASE_URL` or API keys for Gemini/OpenAI.
*   **Google Gemini API Key**: **Required** for vision features - Get yours at [Google AI Studio](https://makersuite.google.com/app/apikey).
*   **Spotify**: Add Client ID/Secret for music control.
*   **Assistant Name**: Customize your wake word (default: "Spitch").

### 3. Run
```bash
python main.py
```
This launches the modern web UI and starts the voice listener.

---

## 🎤 Capabilities & Examples

### 🧠 Intelligent Conversation
> **User**: "I need to calculate the budget for my trip."
> **Spitch**: Opens Calculator.
> **User**: "It's 500 for flight plus 300 for hotel."
> **Spitch**: Types "500+300" into Calculator.
> **User**: "Close it."
> **Spitch**: Closes Calculator.

### 👁️ **NEW: Vision & Image Understanding**
> **User**: *[Uploads screenshot of code]* "What does this code do?"
> **Spitch**: "This Python code defines a function that calculates the Fibonacci sequence using recursion..."

> **User**: "Take a screenshot and tell me what's on my screen."
> **Spitch**: *[Captures screen]* "I see a web browser with a GitHub repository open, showing the README file..."

> **User**: *[Uploads diagram]* "Explain this architecture."
> **Spitch**: "This diagram shows a microservices architecture with..."

### 🌐 Browser & Web Tasks
*   "Open Gemini in browser and search for AI news."
*   "Launch ChatGPT in my browser."
*   "Search for 'best pizza near me' on Google."

### 📂 File Management
*   "Organize all files in my Downloads folder."
*   "Find duplicate images in Pictures."
*   "Show me the files I worked on yesterday."

### 💻 Developer Workflow
*   "What's the status of this repo?"
*   "Commit all changes with message 'Fixed login bug'."
*   "Run 'npm install' for me."

### 🎵 Media & Entertainment
*   "Play 'Bohemian Rhapsody' on Spotify."
*   "Find a tutorial on Python decorators on YouTube."
*   "Set volume to 50%."

### 🔮 Proactive & System
*   *(Morning)* "Good morning! Should I open your work apps?"
*   *(System Alert)* "Disk space is running low (92%). Should we clean temporary files?"

### ⚙️ **NEW: Settings & Customization**
*   Click the **⚙️ Gear Icon** to access settings.
*   Change voice, adjust speed, set your location.
*   All preferences are saved automatically.

---

## 🧩 Architecture

### Core Components
*   **`engine/ai_intent_parser.py`**: The "Brain". Uses LLMs to parse complex, non-standard user requests into actionable plans.
*   **`engine/ai_task_agent.py`**: The "Hand". Executes multi-step workflows with retry logic and error recovery.
*   **`engine/session_manager.py`**: The "Memory". Tracks conversation history and context (short-term).
*   **`engine/memory_bank.py`**: The "Long-term Memory". Stores user preferences and learned patterns.
*   **`engine/proactive_assistant.py`**: The "Conscience". Monitors system state and suggests actions.
*   **`engine/file_intelligence.py`**: File system manager.
*   **`engine/dev_tools.py`**: Git and terminal integration.

### **NEW: Advanced Modules**
*   **`engine/skill_registry.py`**: Dynamic skill management system for extensibility.
*   **`engine/vision_agent.py`**: Computer vision capabilities using Gemini Vision API.
*   **`engine/google_gemini.py`**: Multimodal AI integration (text + image processing).
*   **`engine/safety_sandbox.py`**: Command validation and security layer.
*   **`engine/user_prefs.py`**: User settings and preferences management.

### Frontend
*   **`www/index.html`**: Modern, responsive web interface with image upload support.
*   **`www/main.js`**: Frontend logic for chat, voice, and settings.
*   **`www/style.css`**: Custom styling for a premium user experience.

---

## 🛠️ Recent Updates (Phase 6-9)

### Phase 6: Skill Registry System
- Implemented dynamic skill registration and management
- AI now auto-discovers new capabilities
- Centralized skill execution with error handling

### Phase 7: Vision Agent
- Added computer vision using Gemini Vision 1.5 Flash
- Screen capture and analysis capabilities
- Visual question answering

### Phase 8: Safety Sandbox
- Command validation before execution
- Protection against destructive operations
- Secure shell command handling

### Phase 9: Multimodal Chat
- Image upload via chat interface (📎 button)
- Text + image queries to AI
- Base64 encoding for efficient transfer
- Integrated vision processing in chat flow

---

## 📋 Requirements

### Python Dependencies
```
eel
pyttsx3
SpeechRecognition
pyautogui
pygetwindow
requests
beautifulsoup4
pygame
Pillow
```

### System Requirements
- **OS**: Windows 10/11 (primary), macOS/Linux (experimental)
- **Python**: 3.8+
- **Browser**: Chrome, Edge, or Firefox
- **Internet**: Required for AI models (Gemini/OpenAI) and web features

### API Keys (Optional but Recommended)
- **Google Gemini API**: For vision features and advanced AI
- **OpenAI API**: Alternative AI backend
- **Spotify API**: For music control

---

## 🎯 Roadmap

- [ ] **Image Generation**: Add DALL-E/Stable Diffusion integration
- [ ] **Multi-Language Support**: Expand beyond English
- [ ] **Mobile App**: iOS/Android companion app
- [ ] **Cloud Sync**: Sync preferences across devices
- [ ] **Plugin System**: Community-contributed skills marketplace
- [ ] **Advanced Automation**: Workflow recording and playback

---

## 🤝 Contributing

Contributions are welcome! Whether it's a new skill, a bug fix, or a UI enhancement, feel free to open a PR.

### How to Add a New Skill
1. Create your skill function in `engine/features.py` or a new module
2. Register it in `engine/skill_registry.py` using `@skill_registry.register_skill()`
3. The AI will automatically discover and use it!

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Google Gemini**: For powerful multimodal AI capabilities
- **Eel Framework**: For seamless Python-JavaScript integration
- **Bootstrap**: For responsive UI components
- **Community Contributors**: For feedback and feature requests

---

**Made with ❤️ by Sujith Putta**

*Star ⭐ this repo if you find it useful!*
