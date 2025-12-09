# SPITCH AI Assistant - Project Structure

## 📁 Core Files

### Main Application
- `app.py` - Flask web server and API endpoints
- `main.py` - Alternative entry point
- `config.py` - Configuration settings
- `run_spitch.bat` - Windows batch file to start SPITCH

### MCP (Model Context Protocol)
- `mcp_server.py` - MCP server with 9 tools
- `engine/mcp_client.py` - MCP client integration
- `setup_mcp.py` - MCP setup script
- `requirements_mcp.txt` - MCP dependencies

### Requirements
- `requirements.txt` - All Python dependencies
- `requirements_minimal.txt` - Minimal dependencies
- `requirements_mcp.txt` - MCP-specific dependencies

### Data Files
- `spitch_conversations.json` - User learning data
- `spitch.db` - SQLite database

### Documentation
- `README.md` - Project overview
- `USER_MANUAL.txt` - User guide
- `LEARNING_SYSTEM_SUMMARY.md` - Learning system documentation
- `MCP_IMPLEMENTATION.md` - MCP implementation details
- `OLLAMA_SETUP.md` - Ollama setup guide

## 📁 Directories

### `/engine/`
Core engine modules:
- `ai_assistant.py` - AI integration
- `command.py` - Command processing
- `features.py` - Feature implementations
- `advanced_features.py` - Advanced features
- `mcp_client.py` - MCP client

### `/www/`
Web interface:
- `index.html` - Landing page
- `landing.html` - Landing page
- `style.css` - Styles
- `main.js` - JavaScript

### `/www/app/`
Main application interface:
- `index.html` - App interface
- `main.js` - App logic
- `style.css` - App styles
- `manifest.json` - PWA manifest

### `/vosk-model-small-en-us-0.15/`
Voice recognition model

### `/whisper_models/`
Whisper AI models

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_mcp.txt
   ```

2. Start SPITCH:
   ```bash
   python app.py
   ```
   Or use:
   ```bash
   run_spitch.bat
   ```

3. Open browser:
   ```
   http://localhost:5000
   ```

## ✨ MCP Features

MCP provides 9 powerful tools:
- ⏰ Current time
- 🧮 Calculator
- 💻 System info
- 🚀 Open applications
- 📸 Screenshots
- 📚 Learning data
- 🔍 Web search
- 🌤️ Weather
- 🎵 Music control

## 📝 Notes

- All test files have been removed
- All debug files have been removed
- Project is clean and production-ready
- MCP is fully installed and operational
