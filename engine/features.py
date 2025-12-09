import os
import re
import webbrowser
import urllib.parse
try:
    import pygame
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio playback not available - pygame not installed")
import eel
import requests
import json
import datetime
import subprocess
import time
from engine.speak_utils import speak
import difflib
from bs4 import BeautifulSoup

from engine.config import ASSISTANT_NAME
import pyautogui
import pygetwindow as gw
from engine.ai_assistant import spitch_ai
#sound function for playing sound
def playAssistantSound():
    if AUDIO_AVAILABLE:
        try:
            music_dir = "www\\assets\\audio\\start_sound.mp3"
            pygame.mixer.music.load(music_dir)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Could not play start sound: {e}")

#click sound for mic button
@eel.expose
def playClickSound():
    if AUDIO_AVAILABLE:
        try:
            music_dir = "www\\assets\\audio\\click_sound.mp3"
            pygame.mixer.music.load(music_dir)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Could not play click sound: {e}")

# --- Settings Management ---
from engine.user_prefs import load_settings, save_setting
from engine.speak_utils import get_voice_options # Expose this

@eel.expose
def get_all_settings():
    """Get all user settings"""
    return load_settings()

@eel.expose
def save_all_settings(settings):
    """Save multiple settings at once"""
    try:
        for key, value in settings.items():
            save_setting(key, value)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

 

def get_installed_applications():
    """Discover all installed applications on Windows"""
    apps = {}
    
    # Common built-in Windows applications
    common_apps = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'paint': 'mspaint.exe',
        'wordpad': 'wordpad.exe',
        'chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'edge': 'msedge.exe',
        'explorer': 'explorer.exe',
        'control panel': 'control.exe',
        'task manager': 'taskmgr.exe',
        'cmd': 'cmd.exe',
        'command prompt': 'cmd.exe',
        'powershell': 'powershell.exe',
        'settings': 'ms-settings:',
        'file explorer': 'explorer.exe'
    }
    apps.update(common_apps)
    
    # Scan Start Menu for installed applications
    start_menu_paths = [
        os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
        os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
    ]
    
    for start_menu in start_menu_paths:
        if os.path.exists(start_menu):
            try:
                for root, dirs, files in os.walk(start_menu):
                    for file in files:
                        if file.endswith('.lnk'):
                            app_name = file.replace('.lnk', '').lower()
                            # Clean up common suffixes
                            app_name = app_name.replace(' - shortcut', '')
                            full_path = os.path.join(root, file)
                            apps[app_name] = full_path
            except Exception as e:
                print(f"Error scanning Start Menu: {e}")
    
    # Scan Program Files for common executables
    program_files = [
        os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
        os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs')
    ]
    
    for pf_dir in program_files:
        if os.path.exists(pf_dir):
            try:
                for item in os.listdir(pf_dir):
                    item_path = os.path.join(pf_dir, item)
                    if os.path.isdir(item_path):
                        # Look for .exe files in the directory
                        for file in os.listdir(item_path):
                            if file.endswith('.exe'):
                                app_name = file.replace('.exe', '').lower()
                                apps[app_name] = os.path.join(item_path, file)
            except Exception as e:
                print(f"Error scanning {pf_dir}: {e}")
    
    return apps

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "").strip().lower()
    print(f"[openCommand] Query after cleaning: '{query}'")
    
    if query != "":
        try:
            # Get all installed applications
            print("[openCommand] Discovering installed applications...")
            installed_apps = get_installed_applications()
            print(f"[openCommand] Found {len(installed_apps)} applications")
            
            # Try fuzzy matching with installed apps
            match = difflib.get_close_matches(query, list(installed_apps.keys()), n=1, cutoff=0.6)
            print(f"[openCommand] Fuzzy match result: {match}")
            
            if match:
                matched_name = match[0]
                app_path = installed_apps[matched_name]
                speak(f"Opening {matched_name}")
                print(f"[openCommand] Opening: {app_path}")
                
                try:
                    # Use different methods depending on file type
                    if app_path.endswith('.lnk'):
                        # For shortcuts, use start command
                        os.system(f'start "" "{app_path}"')
                    elif app_path.startswith('ms-'):
                        # For Windows settings URIs
                        os.system(f'start {app_path}')
                    else:
                        # For executables
                        subprocess.Popen(app_path)
                    return
                except Exception as e:
                    print(f"[openCommand] Error opening {matched_name}: {e}")
                    speak(f"Sorry, I couldn't open {matched_name}. Error: {str(e)}")
                return
            
            # If no match found, try direct execution
            print(f"[openCommand] No match found, trying direct execution...")
            speak(f"Trying to open {query}")
            try:
                os.system('start "" "' + query + '"')
            except Exception as e:
                speak(f"Sorry, I couldn't open {query}. Please make sure the application is installed or try a different name.")
                print(f"[openCommand] Direct execution failed: {e}")
        except Exception as e:
            speak(f"Something went wrong while trying to open {query}: {str(e)}")
            print(f"[openCommand] Error: {e}")
    else:
        speak("Please specify what you would like me to open.")




def PlayYoutube(query):
    query_lower = query.lower()
    # If the command is a search
    if re.search(r'(search|find) (.+?) on youtube', query_lower):
        match = re.search(r'(search|find) (.+?) on youtube', query_lower)
        search_term = match.group(2).strip()
        print(f"[YouTube] Search: {search_term}")
        speak(f"Searching YouTube for {search_term}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")
    # If the command is to play
    elif re.search(r'play (.+?) on youtube', query_lower):
        match = re.search(r'play (.+?) on youtube', query_lower)
        search_term = match.group(1).strip()
        print(f"[YouTube] Play: {search_term}")
        speak(f"Playing {search_term} on YouTube")
        # Get the top video result
        try:
            url = f"https://www.youtube.com/results?search_query={search_term}&sp=EgIQAQ%253D%253D"  # Filter for videos only
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.startswith('/watch'):
                    video_url = f"https://www.youtube.com{href}"
                    webbrowser.open(video_url)
                    return
            # Fallback: open search page if no video found
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")
        except Exception as e:
            print(f"Error finding YouTube video: {e}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")
    # Fallback: open search page
    else:
        search_term = query_lower.replace('play', '').replace('search', '').replace('on youtube', '').strip()
        print(f"[YouTube] Fallback Search/Play: {search_term}")
        speak(f"Searching YouTube for {search_term}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")

def toggle_youtube_playback(action, speak_func=None):
    """Pauses or resumes a YouTube video."""
    try:
        # Find windows with "YouTube" in the title
        yt_windows = gw.getWindowsWithTitle('YouTube')
        if not yt_windows:
            if speak_func:
                speak_func("I couldn't find a YouTube window to control.")
            return

        # Activate the first YouTube window found
        yt_window = yt_windows[0]
        if not yt_window.isActive:
            yt_window.activate()
            time.sleep(0.5)

        # Press 'k' to toggle play/pause
        pyautogui.press('k')
        
        if speak_func:
            if action == 'pause':
                speak_func("YouTube video paused.")
            elif action == 'resume':
                speak_func("YouTube video resumed.")
    except Exception as e:
        print(f"Error toggling YouTube playback: {e}")
        if speak_func:
            speak_func("Sorry, I couldn't control the YouTube video.")


def handle_youtube_inquiry(query, speak_func):
    """Handles advanced YouTube-related inquiries using AI or direct logic for community/content/analytics prompts."""
    # List of community/content/analytics keywords
    yt_community_keywords = [
        'poll', 'community post', 'call to action', 'ask my audience', 'ideas for polls',
        'video script', 'thumbnail', 'shorts concept', 'video description', 'title ideas',
        'analyze performance', 'best time to post', 'content calendar', 'seo strategies',
        'optimize my videos', 'monetization requirements', 'passive income', 'brand sponsorships'
    ]
    if any(k in query.lower() for k in yt_community_keywords):
        speak_func("Let me help you with YouTube creator advice.")
        generative_system_prompt = (
            "You are a helpful and creative AI assistant specializing in YouTube. "
            "Provide a detailed, actionable, and creative response for the following creator request. "
            "Give practical tips, examples, and step-by-step advice. Do not output JSON."
        )
        try:
            ai_result = spitch_ai.process_command(query, system_prompt_override=generative_system_prompt, model='tinyllama')
            ai_response = ai_result.get("response")
            if ai_response:
                speak_func(ai_response)
            else:
                speak_func("I'm sorry, I couldn't generate a creative response for that YouTube prompt.")
        except Exception as e:
            print(f"AI processing error for YouTube community/content inquiry: {e}")
            speak_func("I'm having trouble connecting to my AI services to answer that question.")
        return
    # Fallback to original AI handling for other YouTube inquiries
    speak_func("Let me look into that for you.")
    generative_system_prompt = "You are a helpful and creative AI assistant specializing in YouTube. Provide a detailed and insightful response to the user's request. Do not output JSON."
    try:
        ai_result = spitch_ai.process_command(query, system_prompt_override=generative_system_prompt, model='tinyllama')
        ai_response = ai_result.get("response")
        if ai_response:
            speak_func(ai_response)
        else:
            speak_func("I'm sorry, I had trouble formulating a response for that.")
    except Exception as e:
        print(f"AI processing error for YouTube inquiry: {e}")
        speak_func("I'm having trouble connecting to my AI services to answer that question.")


def extract_yt_term(command):
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None