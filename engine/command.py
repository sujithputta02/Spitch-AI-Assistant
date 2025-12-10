import time
import pyttsx3
import json
import eel
import datetime
import webbrowser
import os
import subprocess
import requests
import re
import sys
# Try to import speech recognition with PyAudio fallback handling
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    print("[OK] Speech recognition available")
except ImportError as e:
    print(f"[WARNING] Speech recognition not available: {e}")
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

# Helper function to safely display messages (works with both eel and Flask)
def safe_display_message(message):
    """Safely display message in UI or console"""
    try:
        import eel
        eel.DisplayMessage(message)
    except (ImportError, AttributeError, Exception):
        print(f"[UI] {message}")  # Fallback to console
import difflib

# Imports for Whisper (optional)
try:
    import whisper
    import torch
    import numpy as np
    WHISPER_AVAILABLE = True
    print("[OK] Whisper available for speech recognition")
except ImportError as e:
    print(f"[WARNING] Whisper not available: {e}")
    print("   Speech recognition will use Google only")
    WHISPER_AVAILABLE = False
    whisper = None
    torch = None
    np = None

from engine.advanced_features import *
from engine.spotify_api import search_and_play_song, pause_music, resume_music, handle_spotify_inquiry
from engine.ai_assistant import spitch_ai
from engine.speak_utils import speak
from engine.features import openCommand, PlayYoutube, toggle_youtube_playback, handle_youtube_inquiry
from engine.weather import get_weather
from engine.user_prefs import set_user_location

# Import AI Task Agent for skill-based command execution
try:
    from engine.ai_task_agent import ai_task_agent
    AI_TASK_AGENT_AVAILABLE = True
    print("[OK] AI Task Agent available")
except ImportError as e:
    print(f"[WARNING] AI Task Agent not available: {e}")
    AI_TASK_AGENT_AVAILABLE = False
    ai_task_agent = None

# --- WHISPER SPEECH RECOGNITION SETUP ---
if WHISPER_AVAILABLE:
    # Check if a CUDA-enabled GPU is available, otherwise use CPU
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Whisper using device: {DEVICE}")

    # Load the Whisper model. 
    # "base" is a good starting point. Other options: "tiny", "small", "medium", "large"
    print("Loading Whisper model (base)...")
    model = whisper.load_model("base", device=DEVICE, download_root="whisper_models")
    print("Whisper model loaded.")
else:
    DEVICE = "cpu"
    model = None


@eel.expose
def takeCommand():
    """Takes microphone input from the user and returns string output using Google Speech Recognition first, then Whisper (small) as fallback."""
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("Speech recognition not available - PyAudio not installed")
        safe_display_message("Microphone not available. Please use text input instead.")
        return ""
    
    try:
        r = sr.Recognizer()
        with sr.Microphone(sample_rate=16000) as source:
            print("Listening for voice command...")
            r.pause_threshold = 0.8
            r.adjust_for_ambient_noise(source, duration=3)
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                print("Listening timed out.")
                safe_display_message("Listening timed out.")
                return ""
            except Exception as e:
                print(f"Microphone error: {e}")
                safe_display_message(f"Microphone error: {e}")
                return ""
    except Exception as e:
        print(f"PyAudio/Microphone not available: {e}")
        safe_display_message("Microphone not available. Please use text input instead.")
        return ""

    # Try Google Speech Recognition first
    try:
        google_lang = SUPPORTED_LANGUAGES[VOICE_LANGUAGE]['google_code']
        query = r.recognize_google(audio, language=google_lang)
        print(f"Recognized (Google {google_lang}): {query}")
        safe_display_message(f"(Google) You said: {query}")
        return query.lower()
    except Exception as e:
        print(f"Google recognition error: {e}")
        safe_display_message(f"Google recognition error: {e}. Trying Whisper fallback...")

    # Fallback: Whisper (small) - only if available
    if WHISPER_AVAILABLE:
        try:
            print("Loading Whisper model (small)...")
            model = whisper.load_model("small", device=DEVICE, download_root="whisper_models")
            print("Whisper model loaded.")
            audio_data = audio.get_raw_data()
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            whisper_lang = SUPPORTED_LANGUAGES[VOICE_LANGUAGE]['whisper_code']
            result = model.transcribe(audio_np, fp16=(DEVICE == "cuda"), language=whisper_lang)
            query = result['text']
            print(f"Recognized (Whisper): {query}")
            safe_display_message(f"(Whisper) You said: {query}")
            return query.lower()
        except Exception as e:
            print(f"Whisper recognition error: {e}")
            safe_display_message(f"Whisper recognition error: {e}")
            return ""
    else:
        print("Whisper not available - speech recognition failed")
        safe_display_message("Speech recognition failed - Whisper not installed")
        return ""


# Multi-language support
SUPPORTED_LANGUAGES = {
    'en-US': {'name': 'English', 'whisper_code': 'en', 'google_code': 'en-US'},
    'te-IN': {'name': 'తెలుగు (Telugu)', 'whisper_code': 'te', 'google_code': 'te-IN'},
    'kn-IN': {'name': 'ಕನ್ನಡ (Kannada)', 'whisper_code': 'kn', 'google_code': 'kn-IN'},
    'ml-IN': {'name': 'മലയാളം (Malayalam)', 'whisper_code': 'ml', 'google_code': 'ml-IN'},
    'hi-IN': {'name': 'हिन्दी (Hindi)', 'whisper_code': 'hi', 'google_code': 'hi-IN'}
}

VOICE_LANGUAGE = 'en-US'  # Default to English

@eel.expose
def set_voice_language(lang_code):
    global VOICE_LANGUAGE
    if lang_code in SUPPORTED_LANGUAGES:
        VOICE_LANGUAGE = lang_code
        print(f"[Voice] Language set to: {SUPPORTED_LANGUAGES[lang_code]['name']} ({lang_code})")
        return True
    else:
        print(f"[Voice] Unsupported language: {lang_code}")
        return False

@eel.expose
def get_supported_languages():
    """Return list of supported languages for the UI"""
    return SUPPORTED_LANGUAGES

@eel.expose
def get_current_language():
    """Return current language setting"""
    return VOICE_LANGUAGE

def process_direct_command(query):
    """Process commands directly without AI for faster response, now with fuzzy matching."""
    query_lower = query.lower().strip()
    print(f"Processing direct command: {query_lower}")

    # Fuzzy matching helpers
    def fuzzy_match(query, options, cutoff=0.6):
        match = difflib.get_close_matches(query, options, n=1, cutoff=cutoff)
        return match[0] if match else None

    # Keywords for advanced YouTube inquiries
    youtube_inquiry_keywords = [
        'videos about', 'most-watched youtube', 'beginner tutorials', 'trending youtube shorts',
        'recommend youtubers', 'title ideas', 'video script', 'thumbnail ideas', 'shorts concept',
        'video description', 'ask my audience', 'call to action', 'community post', 'ideas for polls',
        'analyze performance', 'best time to post', 'content calendar', 'seo strategies', 
        'optimize my videos', 'monetization requirements', 'passive income', 'brand sponsorships'
    ]
    if any(fuzzy_match(query_lower, [k], 0.8) for k in youtube_inquiry_keywords):
        handle_youtube_inquiry(query, speak_func=speak)
        return True

    # Keywords for advanced Spotify inquiries
    spotify_inquiry_keywords = [
        'music similar to', 'trending songs', 'top 10 songs', 'top songs on spotify', 'chill music',
        'indie rock albums', 'recommend a playlist', 'create a playlist', 'add this song',
        'shuffle my playlist', 'remove song', 'sort my playlist', 'most played song', 
        'discover weekly', 'songs i\'ve liked', 'build a playlist', 'top genre', 'play something',
        'feeling sad', 'i need a boost', 'motivational tracks', 'true crime podcast', 'latest episode',
        'trending podcasts', 'podcast under', 'listening stats', 'my top 5 songs', 'most listened-to artists'
    ]
    if 'spotify' in query_lower and any(fuzzy_match(query_lower, [k], 0.8) for k in spotify_inquiry_keywords):
        handle_spotify_inquiry(query, speak_func=speak)
        return True

    # Fuzzy match for time and date
    if any(phrase in query_lower for phrase in ['what time is it', 'current time', 'time now']) or fuzzy_match(query_lower, ['time', 'what time'], 0.8):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        return True
    elif fuzzy_match(query_lower, ['date', 'what date', 'today'], 0.8):
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {current_date}")
        return True

    # YouTube/Spotify music commands (moved up)
    elif 'youtube' in query_lower:
        PlayYoutube(query)
        return True
    elif 'play' in query_lower and 'spotify' in query_lower:
        song_name = query_lower.replace('play', '').replace('on spotify', '').strip()
        speak(f"Playing {song_name} on Spotify.")
        search_and_play_song(song_name, speak_func=speak)
        return True

    # Fuzzy match for pause/resume
    elif fuzzy_match(query_lower, ['pause', 'pause the song', 'pause music', 'pause youtube'], 0.7):
        if 'youtube' in query_lower:
            toggle_youtube_playback('pause', speak_func=speak)
        else:
            pause_music(speak_func=speak)
        return True
    elif fuzzy_match(query_lower, ['resume', 'continue', 'resume music', 'resume the music', 'resume youtube'], 0.7):
        if 'youtube' in query_lower:
            toggle_youtube_playback('resume', speak_func=speak)
        else:
            resume_music(speak_func=speak)
        return True

    # Web search commands (now after YouTube)
    elif 'google' in query_lower or (any(fuzzy_match(query_lower, [w], 0.8) for w in ['search', 'find']) and 'youtube' not in query_lower):
        search_term = query_lower
        for word in ['search', 'for', 'google', 'find', 'on', 'the', 'web']:
            search_term = search_term.replace(word, '')
        search_term = search_term.strip()
        if search_term:
            speak(f"Searching for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
            return True

    # Calculator commands
    elif any(fuzzy_match(query_lower, [w], 0.8) for w in ['calculate', 'math', 'what is']) and any(op in query_lower for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
        math_pattern = r'(\d+\s*[\+\-\*\/]\s*\d+)'
        match = re.search(math_pattern, query)
        if match:
            expression = match.group(1)
            try:
                result = eval(expression)
                speak(f"The result is {result}")
                return True
            except:
                speak("I couldn't calculate that. Please try again.")
                return True

    # Screenshot commands
    elif any(fuzzy_match(query_lower, [w], 0.8) for w in ['screenshot', 'capture', 'screen']):
        take_screenshot(speak_func=speak)
        return True

    # System info commands (including CPU usage)
    elif any(fuzzy_match(query_lower, [w], 0.8) for w in ['system', 'computer', 'info', 'specs', 'cpu', 'memory', 'ram']):
        get_system_info(speak_func=speak, query=query_lower)
        return True
    elif 'cpu usage' in query_lower or ('cpu' in query_lower and any(w in query_lower for w in ['usage', 'use', 'percent'])):
        get_system_info(speak_func=speak, query=query_lower)
        return True

    # Set location command
    elif fuzzy_match(query_lower, ['set my location to'], 0.8):
        city = query_lower.replace("set my location to", "").strip()
        if city:
            set_user_location(city.title(), speak_func=speak)
        else:
            speak("Please tell me which city to set as your location.")
        return True

    # Weather commands
    elif any(fuzzy_match(query_lower, [w], 0.8) for w in ['weather', 'forecast']):
        forecast_days = 1
        match = re.search(r"(\d+)\s*day", query_lower)
        if match:
            forecast_days = int(match.group(1))
        elif "week" in query_lower:
            forecast_days = 7
        get_weather(query=query_lower, speak_func=speak, forecast_days=forecast_days)
        return True

    # Joke commands
    elif any(fuzzy_match(query_lower, [w], 0.8) for w in ['joke', 'funny', 'humor']):
        speak("Here's a joke for you: Why don't scientists trust atoms? Because they make up everything!")
        return True

    # Help commands
    elif any(fuzzy_match(query_lower, [w], 0.8) for w in ['help', 'what can you do', 'capabilities']):
        speak("I can help you with: opening apps, playing music on YouTube or Spotify, web searches, telling time and date, taking screenshots, checking weather, and more!")
        return True

    # Open application commands
    elif 'open' in query_lower:
        openCommand(query)
        return True

    # WhatsApp LLM/creative message handling
    if 'whatsapp' in query_lower and any(w in query_lower for w in ['message', 'draft', 'send']):
        draft_whatsapp_message(query, speak_func=speak)
        return True

    return False

# Import AI Task Agent
try:
    from engine.ai_task_agent import ai_task_agent
    AI_TASK_AGENT_AVAILABLE = True
    print("[OK] AI Task Agent available")
except ImportError:
    AI_TASK_AGENT_AVAILABLE = False
    ai_task_agent = None
    print("[WARNING] AI Task Agent not available")

# Initialize AI Intent Parser for JARVIS-level understanding
try:
    from engine.ai_intent_parser import initialize_parser
    from engine.ai_assistant import spitch_ai
    
    ai_intent_parser = initialize_parser(spitch_ai)
    print("[OK] AI Intent Parser initialized - JARVIS-level NLU enabled")
except Exception as e:
    print(f"[WARNING] AI Intent Parser initialization failed: {e}")

# Initialize Session Manager and Memory Bank for learning
try:
    from engine.session_manager import session_manager
    from engine.memory_bank import memory_bank
    
    print("[OK] Session Manager initialized - Conversation tracking enabled")
    print("[OK] Memory Bank initialized - Learning system active")
    
    # Load previous session if exists
    if session_manager.load_session():
        print("[OK] Previous session loaded")
    
    # Print memory summary
    summary = memory_bank.get_memory_summary()
    print(f"[MEMORY] Learned from {summary['total_successful_commands']} successful commands")
    if summary['most_used_apps']:
        top_app = summary['most_used_apps'][0]
        print(f"[MEMORY] Most used app: {top_app[0]} ({top_app[1]} times)")
    
except Exception as e:
    print(f"[WARNING] Session/Memory initialization failed: {e}")

# Initialize Proactive Assistant and Pattern Tracker for JARVIS-level anticipation
try:
    from engine.proactive_assistant import proactive_assistant
    from engine.pattern_tracker import pattern_tracker
    
    print("[OK] Proactive Assistant initialized - Smart suggestions enabled")
    print("[OK] Pattern Tracker initialized - Learning user habits")
    
    # Get system status
    status = proactive_assistant.get_system_status()
    print(f"[SYSTEM] CPU: {status.get('cpu_percent', 0):.1f}%, Memory: {status.get('memory_percent', 0):.1f}%, Disk: {status.get('disk_percent', 0):.1f}%")
    print(f"[TIME] Current period: {status.get('time_of_day', 'unknown')}")
    
    # Get proactive suggestions
    suggestions = proactive_assistant.get_proactive_suggestions()
    if suggestions:
        print(f"[PROACTIVE] {len(suggestions)} suggestions available")
        for suggestion in suggestions:
            print(f"  💡 {suggestion}")
    
except Exception as e:
    print(f"[WARNING] Proactive features initialization failed: {e}")

@eel.expose
def processTextCommand(query, image_base64=None):
    """Process text commands with optional image attachment. Returns the spoken/text response as a string."""
    print(f"[TextCommand] Received: {query}")
    safe_display_message(f"Processing command: {query[:50]}...") # DEBUG
    
    if image_base64:
        print("[TextCommand] Image attachment detected")
        safe_display_message("Image attachment received.") # DEBUG
    
    if not query and not image_base64:
        speak("Please enter a command or attach an image.")
        safe_display_message("Please enter a command or attach an image.")
        return "Please enter a command."

    # --- VISION PROCESSING ---
    if image_base64:
        from engine.google_gemini import spitch_gemini
        import base64
        
        print(f"[Vision] Processing vision query: '{query}'")
        speak("Let me look at that image for you.")
        
        try:
            # Clean Base64 string (remove data:image/png;base64, prefix if present)
            if ',' in image_base64:
                header, encoded = image_base64.split(',', 1)
            else:
                encoded = image_base64
            
            image_bytes = base64.b64decode(encoded)
            
            # Use Gemini Vision
            # Default prompt if query is empty
            if not query:
                query = "Describe this image in detail."
                
            response = spitch_gemini.process_vision_query(query, image_bytes)
            
            if response:
                speak(response)
                safe_display_message(response)
                return response
            else:
                msg = "I couldn't analyze the image. Please try again."
                speak(msg)
                return msg
                
        except Exception as e:
            print(f"[Vision] Error processing image: {e}")
            import traceback
            traceback.print_exc()
            msg = f"Error analyzing image: {str(e)}"
            safe_display_message(f"Vision Error: {str(e)}") # DEBUG
            speak("Sorry, I encountered an error checking that image.")
            return msg

    # IMPORTANT: Check for complex multi-step commands FIRST before direct command processing
    # This prevents commands like "open notepad, write text" from being treated as simple "open" commands
    complex_patterns = [
        ('open' in query.lower() and 'write' in query.lower()),
        ('open' in query.lower() and 'save' in query.lower()),
        ('open' in query.lower() and 'calculate' in query.lower()),  # NEW: "open calculator and calculate"
        ('open' in query.lower() and 'and' in query.lower() and any(word in query.lower() for word in ['write', 'save', 'type', 'calculate', 'search', 'play'])),  # NEW: open X and do Y
        ('create file' in query.lower() or 'write file' in query.lower()),
        (query.lower().count(',') >= 1 and any(word in query.lower() for word in ['write', 'save', 'type'])),  # Comma with action words
        ('search' in query.lower() and ('google' in query.lower() or 'web' in query.lower())),  # NEW: search commands
        ('play' in query.lower() and 'youtube' in query.lower()),  # NEW: play on youtube
        ('calculate' in query.lower() or 'what is' in query.lower()),  # NEW: calculations
        ('take screenshot' in query.lower() or 'screenshot' in query.lower()),  # NEW: screenshots
        ('generate' in query.lower() and 'image' in query.lower()),  # NEW: image generation
        ('create' in query.lower() and ('image' in query.lower() or 'picture' in query.lower())),  # NEW: create image/picture
        ('make' in query.lower() and ('image' in query.lower() or 'picture' in query.lower())),  # NEW: make image/picture
        # BROWSER AUTOMATION PATTERNS
        ('open browser' in query.lower() or 'start browser' in query.lower()),  # NEW: browser automation
        ('close browser' in query.lower()),  # NEW: close browser
        ('fill' in query.lower() and any(word in query.lower() for word in ['form', 'field', 'box', 'input'])),  # NEW: form filling
        ('click' in query.lower() and any(word in query.lower() for word in ['button', 'link', 'element'])),  # NEW: clicking elements
        ('extract' in query.lower() and 'text' in query.lower()),  # NEW: text extraction
        ('screenshot' in query.lower() and 'page' in query.lower()),  # NEW: page screenshot
        ('navigate to' in query.lower() or 'go to' in query.lower()),  # NEW: navigation
    ]
    
    if AI_TASK_AGENT_AVAILABLE and any(complex_patterns):
        print("[TextCommand] Detected complex multi-step command, using AI Task Agent")
        try:
            result = ai_task_agent.execute_task(query, speak_func=speak)
            if result['success']:
                safe_display_message(result['message'])
                return result['message']
            else:
                # If AI Task Agent couldn't handle it, fall through to normal processing
                print(f"[TextCommand] AI Task Agent couldn't handle: {result['message']}")
        except Exception as e:
            print(f"[TextCommand] AI Task Agent error: {e}")
    
    # Now try direct command processing (for simple commands)
    try:
        direct_result = process_direct_command(query)
        print(f"[TextCommand] Direct command result: {direct_result}")
        if direct_result:
            # If direct command handled, return a more specific message
            return "Direct command executed successfully."
    except Exception as e:
        print(f"[TextCommand] Error in direct command processing: {e}")

    # Check if this is a compound command (contains 'and')
    if ' and ' in query.lower():
        print("[TextCommand] Detected compound command with 'and'")
        # Split by 'and' and process each part
        parts = [part.strip() for part in query.split(' and ')]
        results = []
        
        for i, part in enumerate(parts):
            print(f"[TextCommand] Processing part {i+1}/{len(parts)}: {part}")
            
            # First, try direct command processing for faster response
            try:
                direct_result = process_direct_command(part)
                print(f"[TextCommand] Part {i+1} direct command result: {direct_result}")
                if direct_result:
                    results.append(f"Part {i+1} completed")
                    continue
            except Exception as e:
                print(f"[TextCommand] Error in direct command processing for part {i+1}: {e}")
            
            # If direct processing didn't work, try AI processing for this part
            try:
                print(f"[TextCommand] Trying AI processing for part {i+1}...")
                
                # Try quick response first
                quick_response = spitch_ai.get_quick_response(part)
                if quick_response:
                    print(f"[TextCommand] Quick Response for part {i+1}: {quick_response}")
                    speak(quick_response)
                    safe_display_message(quick_response)
                    results.append(quick_response)
                    continue
                
                # Use full AI processing
                ai_result = spitch_ai.process_command(part, speak_func=speak, language=VOICE_LANGUAGE)
                intent = ai_result["intent"]
                ai_response = ai_result["response"]
                
                speak(ai_response)
                safe_display_message(ai_response)
                results.append(ai_response)
                
            except Exception as e:
                print(f"[TextCommand] AI processing failed for part {i+1}: {e}")
                results.append(f"Could not process: {part}")
        
        # Return combined results
        final_response = " ".join(results)
        return final_response

    # Single command processing (original logic)
    # First, try direct command processing for faster response
    try:
        direct_result = process_direct_command(query)
        print(f"[TextCommand] Direct command result: {direct_result}")
        if direct_result:
            # If direct command handled, return a more specific message
            return "Direct command executed successfully."
    except Exception as e:
        print(f"[TextCommand] Error in direct command processing: {e}")

    # If direct processing didn't work, try AI processing
    try:
        print("[TextCommand] Trying AI processing...")
        
        # Try quick response first
        quick_response = spitch_ai.get_quick_response(query)
        if quick_response:
            print(f"[TextCommand] Quick Response: {quick_response}")
            speak(quick_response)
            safe_display_message(quick_response)
            return quick_response
        
        # Use full AI processing
        ai_result = spitch_ai.process_command(query, speak_func=speak, language=VOICE_LANGUAGE)
        intent = ai_result["intent"]
        ai_response = ai_result["response"]
        ai_source = ai_result.get("ai_source", "Unknown")
        
        print(f"[TextCommand] AI Source: {ai_source}")
        print(f"[TextCommand] AI Intent: {intent}")
        print(f"[TextCommand] AI Response: {ai_response}")
        
        # Check if this is a fallback response
        if intent.get("type") == "fallback":
            print("[TextCommand] AI returned fallback response, trying alternative processing...")
            # Try to handle simple conversational queries
            if any(word in query.lower() for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
                response = "Hello! How can I help you today?"
                speak(response)
                safe_display_message(response)
                return response
            elif any(word in query.lower() for word in ['how are you', 'how do you do']):
                response = "I'm doing great! Ready to help you with any tasks or questions."
                speak(response)
                safe_display_message(response)
                return response
            elif any(word in query.lower() for word in ['thank you', 'thanks']):
                response = "You're welcome! Is there anything else I can help you with?"
                speak(response)
                safe_display_message(response)
                return response
        
        # Return the AI response
        speak(ai_response)
        safe_display_message(ai_response)
        return ai_response
        
    except Exception as e:
        print(f"[TextCommand] AI processing failed: {e}")
        # Final fallback
        fallback_msg = "I'm having trouble processing that command right now. Could you try rephrasing it or try a different command?"
        speak(fallback_msg)
        safe_display_message(fallback_msg)
        return fallback_msg

@eel.expose
def test_command():
    """Test function to verify basic command processing is working"""
    speak("Testing command processing. This should work immediately.")
    return "Test successful"

@eel.expose
def get_real_system_stats():
    """Get real-time system statistics for the UI HUD."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        # Convert total memory to GB with 1 decimal place
        ram_gb = f"{memory.total / (1024**3):.1f}G"
        ram_percent = memory.percent
        return {'cpu': cpu, 'ram_total': ram_gb, 'ram_percent': ram_percent}
    except Exception as e:
        print(f"Error getting system stats: {e}")
        return {'cpu': 0, 'ram_total': '0G', 'ram_percent': 0}


@eel.expose
def allCommands():
    query = takeCommand()
    print(f"Processing command: {query}")

    if not query:
        speak("I didn't catch that. Could you please repeat?")
        return

    # Use the same processing for voice commands
    processTextCommand(query)

def test_new_manual_features():
    """Test new features from the user manual: Spotify podcast and YouTube community/content/analytics prompts."""
    test_prompts = [
        # Spotify Podcast
        "Play the latest episode of The Daily podcast on Spotify.",
        "Find a true crime podcast with high ratings on Spotify.",
        # YouTube Community/Content/Analytics
        "Create a poll for my YouTube community.",
        "Give me a call to action for my next video.",
        "Write a YouTube video script intro for AI in healthcare.",
        "Suggest thumbnail ideas for a travel vlog.",
        "Give me ideas for YouTube Shorts concepts about productivity.",
        "Write an engaging video description for a cooking tutorial.",
        "Give me title ideas for a tech review channel.",
        "Analyze the performance of my last YouTube video.",
        "What is the best time to post on YouTube?",
        "Help me create a content calendar for my channel.",
        "What are some YouTube SEO strategies?",
        "How do I optimize my videos for more watch time?",
        "What are the YouTube monetization requirements?",
        "Suggest passive income strategies for a small YouTube creator.",
        "How do I get brand sponsorships for my channel?"
    ]
    print("\n--- Testing new user manual features ---\n")
    for prompt in test_prompts:
        print(f"\n[TEST PROMPT] {prompt}")
        processTextCommand(prompt)
    print("\n--- End of tests ---\n")

    