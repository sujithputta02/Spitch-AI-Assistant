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
import speech_recognition as sr # Keep for Microphone class

# Imports for Whisper
import whisper
import torch
import numpy as np

from engine.advanced_features import *
from engine.spotify_api import search_and_play_song, pause_music, resume_music, handle_spotify_inquiry
from engine.ai_assistant import spitch_ai
from engine.speak_utils import speak
from engine.features import openCommand, PlayYoutube, toggle_youtube_playback, handle_youtube_inquiry
from engine.weather import get_weather
from engine.user_prefs import set_user_location

# --- WHISPER SPEECH RECOGNITION SETUP ---
# Check if a CUDA-enabled GPU is available, otherwise use CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Whisper using device: {DEVICE}")

# Load the Whisper model. 
# "base" is a good starting point. Other options: "tiny", "small", "medium", "large"
print("Loading Whisper model (tiny)...")
model = whisper.load_model("tiny", device=DEVICE, download_root="whisper_models")
print("Whisper model loaded.")


@eel.expose
def takeCommand():
    """Takes microphone input from the user and returns string output using Whisper"""
    r = sr.Recognizer()
    # Whisper expects 16kHz sample rate
    with sr.Microphone(sample_rate=16000) as source:
        print("Listening with Whisper...")
        r.pause_threshold = 0.8
        r.adjust_for_ambient_noise(source, duration=3)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return ""
        except Exception as e:
            print(f"Microphone error: {e}")
            return ""

    print("Recognizing with Whisper...")
    
    try:
        # Get audio data in the format Whisper needs
        audio_data = audio.get_raw_data()
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Transcribe using Whisper
        # Set fp16=False if using CPU
        lang_code = VOICE_LANGUAGE.split('-')[0]
        result = model.transcribe(audio_np, fp16=(DEVICE == "cuda"), language=lang_code)
        query = result['text']

        print(f"Recognized (Whisper): {query}")
        return query.lower()
    except Exception as e:
        print(f"Whisper recognition error: {e}")
        return ""


# Use English for voice recognition
VOICE_LANGUAGE = 'en-US'  # English (Note: This is now less critical as Whisper is multi-lingual)

@eel.expose
def set_voice_language(lang_code):
    global VOICE_LANGUAGE
    VOICE_LANGUAGE = lang_code
    print(f"[Voice] Language set to: {VOICE_LANGUAGE}")

def process_direct_command(query):
    """Process commands directly without AI for faster response"""
    query_lower = query.lower().strip()
    
    print(f"Processing direct command: {query_lower}")

    # Keywords for advanced YouTube inquiries
    youtube_inquiry_keywords = [
        'videos about', 'most-watched youtube', 'beginner tutorials', 'trending youtube shorts',
        'recommend youtubers', 'title ideas', 'video script', 'thumbnail ideas', 'shorts concept',
        'video description', 'ask my audience', 'call to action', 'community post', 'ideas for polls',
        'analyze performance', 'best time to post', 'content calendar', 'seo strategies', 
        'optimize my videos', 'monetization requirements', 'passive income', 'brand sponsorships'
    ]

    if any(keyword in query_lower for keyword in youtube_inquiry_keywords):
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

    if 'spotify' in query_lower and any(keyword in query_lower for keyword in spotify_inquiry_keywords):
        handle_spotify_inquiry(query, speak_func=speak)
        return True
    
    # Time and date commands
    if any(word in query_lower for word in ['time', 'what time']):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        return True
    
    elif any(word in query_lower for word in ['date', 'what date', 'today']):
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
        
    elif 'pause' in query_lower:
        if 'youtube' in query_lower:
            toggle_youtube_playback('pause', speak_func=speak)
        else:
            pause_music(speak_func=speak)
        return True
        
    elif 'resume' in query_lower or 'continue' in query_lower:
        if 'youtube' in query_lower:
            toggle_youtube_playback('resume', speak_func=speak)
        else:
            resume_music(speak_func=speak)
        return True

    # Web search commands (now after YouTube)
    elif 'google' in query_lower or (any(word in query_lower for word in ['search', 'find']) and 'youtube' not in query_lower):
        search_term = query_lower
        # Remove common words
        for word in ['search', 'for', 'google', 'find', 'on', 'the', 'web']:
            search_term = search_term.replace(word, '')
        search_term = search_term.strip()
        if search_term:
            speak(f"Searching for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
            return True
    
    # Calculator commands
    elif any(word in query_lower for word in ['calculate', 'math', 'what is']) and any(op in query_lower for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
        # Extract mathematical expression
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
    elif any(word in query_lower for word in ['screenshot', 'capture', 'screen']):
        take_screenshot(speak_func=speak)
        return True
    
    # System info commands
    elif any(word in query_lower for word in ['system', 'computer', 'info', 'specs']):
        get_system_info(speak_func=speak)
        return True
    
    # Set location command
    elif "set my location to" in query_lower:
        city = query_lower.replace("set my location to", "").strip()
        if city:
            set_user_location(city.title(), speak_func=speak)
        else:
            speak("Please tell me which city to set as your location.")
        return True
    
    # Weather commands
    elif 'weather' in query_lower or 'forecast' in query_lower:
        forecast_days = 1
        # Check for multi-day forecast requests
        match = re.search(r"(\d+)\s*day", query_lower)
        if match:
            forecast_days = int(match.group(1))
        elif "week" in query_lower:
            forecast_days = 7
        
        get_weather(query=query_lower, speak_func=speak, forecast_days=forecast_days)
        return True
    
    # Joke commands
    elif any(word in query_lower for word in ['joke', 'funny', 'humor']):
        speak("Here's a joke for you: Why don't scientists trust atoms? Because they make up everything!")
        return True
    
    # Help commands
    elif any(word in query_lower for word in ['help', 'what can you do', 'capabilities']):
        speak("I can help you with: opening apps, playing music on YouTube or Spotify, web searches, telling time and date, taking screenshots, checking weather, and more!")
        return True
    
    return False

@eel.expose
def processTextCommand(query):
    """Process text commands using direct processing first, then AI as fallback. Returns the spoken/text response as a string."""
    print(f"[TextCommand] Received: {query}")
    if not query:
        speak("Please enter a command.")
        return "Please enter a command."

    # First, try direct command processing for faster response
    try:
        direct_result = process_direct_command(query)
        print(f"[TextCommand] Direct command result: {direct_result}")
        if direct_result:
            # If direct command handled, return a generic or last spoken message
            return "Command processed."
    except Exception as e:
        print(f"[TextCommand] Error in direct command processing: {e}")

    # If direct processing didn't work, try AI processing
    try:
        print("[TextCommand] Trying AI processing...")
        quick_response = spitch_ai.get_quick_response(query)
        if quick_response:
            speak(quick_response)
            return quick_response
        ai_result = spitch_ai.process_command(query, speak_func=speak)
        intent = ai_result["intent"]
        ai_response = ai_result["response"]
        print(f"[TextCommand] AI Intent: {intent}")
        print(f"[TextCommand] AI Response: {ai_response}")
        speak(ai_response)
        return ai_response
    except Exception as e:
        print(f"[TextCommand] AI processing failed: {e}")
        if not process_direct_command(query):
            speak("I'm sorry, I couldn't understand that command. Please try again.")
            return "I'm sorry, I couldn't understand that command. Please try again."
    return "Command processed."

@eel.expose
def test_command():
    """Test function to verify basic command processing is working"""
    speak("Testing command processing. This should work immediately.")
    return "Test successful"

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

    