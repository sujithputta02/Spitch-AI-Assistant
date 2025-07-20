import os
import re
import mysql.connector
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
import difflib
from bs4 import BeautifulSoup

from engine.config import ASSISTANT_NAME
# import pywhatkit as kit  # Commented out to avoid InternetException
import pyautogui
import pygetwindow as gw
from engine.ai_assistant import spitch_ai
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Sujith@20$',
    database='spitch_ai'
)
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
    print(f"[openCommand] Query after cleaning: '{query}'")
    if query != "":
        try:
            # Try to find the application in sys_command table
            cursor.execute('SELECT name, path FROM sys_command')
            sys_commands = cursor.fetchall()
            app_names = [name for name, _ in sys_commands]
            print(f"[openCommand] App names in DB: {app_names}")
            match = difflib.get_close_matches(query, app_names, n=1, cutoff=0.6)
            print(f"[openCommand] Fuzzy match result: {match}")
            if match:
                matched_name = match[0]
                path = [path for name, path in sys_commands if name == matched_name][0]
                speak(f"Opening {matched_name}")
                os.startfile(path)
                return
            # If not found, try to find the URL in web_command table
            cursor.execute('SELECT name, url FROM web_command')
            web_commands = cursor.fetchall()
            web_names = [name for name, _ in web_commands]
            match = difflib.get_close_matches(query, web_names, n=1, cutoff=0.6)
            if match:
                matched_name = match[0]
                url = [url for name, url in web_commands if name == matched_name][0]
                speak(f"Opening {matched_name}")
                webbrowser.open(url)
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
            match = difflib.get_close_matches(query, list(common_apps.keys()), n=1, cutoff=0.6)
            print(f"[openCommand] Fuzzy match in common apps: {match}")
            if match:
                matched_name = match[0]
                speak(f"Opening {matched_name}")
                try:
                    os.system(f'start {common_apps[matched_name]}')
                    return
                except Exception as e:
                    speak(f"Sorry, I couldn't open {matched_name}. Error: {str(e)}")
                return
            # If still not found, try to open using os.system
            speak(f"Trying to open {query}")
            try:
                os.system('start ' + query)
            except Exception as e:
                speak(f"Sorry, I couldn't open {query}. Please make sure the application is installed or try a different name.")
            eel.DisplayMessage(f"No matching application found for '{query}'. Please check the name in your database or try a different command.")
        except Exception as e:
            speak(f"Something went wrong while trying to open {query}: {str(e)}")
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