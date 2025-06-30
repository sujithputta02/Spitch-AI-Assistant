import os
import re
import sqlite3
import webbrowser
import urllib.parse
from playsound import playsound
import eel
import requests
import json
import datetime
import subprocess
import time
from engine.speak_utils import speak

from engine.config import ASSISTANT_NAME
# import pywhatkit as kit  # Commented out to avoid InternetException
import pyautogui
import pygetwindow as gw
from engine.ai_assistant import spitch_ai
from config import DATABASE_PATH


conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()
#sound function for playing sound
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

#click sound for mic button

@eel.expose
def playClickSound():
    music_dir = "www\\assets\\audio\\click_sound.mp3"
    playsound(music_dir)
 

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "").strip().lower()

    if query != "":
        try:
            # Try to find the application in sys_command table
            cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak(f"Opening {query}")
                os.startfile(results[0][0])
                return

            # If not found, try to find the URL in web_command table
            cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()
            
            if len(results) != 0:
                speak(f"Opening {query}")
                webbrowser.open(results[0][0])
                return

            # Try common applications
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
                'powershell': 'powershell.exe'
            }
            
            if query in common_apps:
                speak(f"Opening {query}")
                try:
                    os.system(f'start {common_apps[query]}')
                    return
                except Exception as e:
                    speak(f"Sorry, I couldn't open {query}. Error: {str(e)}")
                return

            # If still not found, try to open using os.system
            speak(f"Trying to open {query}")
            try:
                os.system('start ' + query)
            except Exception as e:
                speak(f"Sorry, I couldn't open {query}. Please make sure the application is installed or try a different name.")

        except Exception as e:
            speak(f"Something went wrong while trying to open {query}: {str(e)}")
    else:
        speak("Please specify what you would like me to open.")



def PlayYoutube(query):
    """Plays a video on YouTube based on the query."""
    # Use regex to extract the search term for 'play ... on youtube' or 'search ... on youtube'
    match = re.search(r'(play|search)\s+(.*?)\s+on\s+youtube', query, re.IGNORECASE)
    if match:
        search_term = match.group(2).strip()
    else:
        # Fallback: remove common words and 'youtube' from the query
        search_term = query.lower()
        for word in ['play', 'search for', 'search', 'on youtube', 'youtube']:
            search_term = search_term.replace(word, '')
        search_term = search_term.strip()
    
    if not search_term:
        speak("Please specify what you want to play or search on YouTube.")
        return

    speak(f"Playing {search_term} on YouTube")
    print(f"[YouTube] Search/Play: {search_term}")
    try:
        # kit.playonyt(search_term)  # Commented out as per instructions
        pass
    except Exception as e:
        print(f"pywhatkit.playonyt failed: {e}")
        speak(f"Couldn't play directly, opening YouTube search for {search_term}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}")

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
            ai_result = spitch_ai.process_command(query, system_prompt_override=generative_system_prompt, model='phi3')
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
        ai_result = spitch_ai.process_command(query, system_prompt_override=generative_system_prompt, model='phi3')
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