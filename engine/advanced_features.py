import requests
import json
import datetime
import webbrowser
import os
import subprocess
import time

def get_weather(city="London", speak_func=None):
    """Get weather information for a city"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        # This would require an API key from a weather service
        # For now, we'll just provide a placeholder
        speak_func(f"I'm sorry, I don't have weather access configured yet. You can check the weather for {city} on weather.com")
        webbrowser.open(f"https://weather.com/search?q={city}")
    except Exception as e:
        speak_func("Sorry, I couldn't get the weather information.")

def search_wikipedia(query, speak_func=None):
    """Search Wikipedia for information"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func(f"Searching Wikipedia for {query}")
        webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
    except Exception as e:
        speak_func("Sorry, I couldn't search Wikipedia.")

def translate_text(text, target_language="es", speak_func=None):
    """Translate text to another language"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func(f"Translating to {target_language}")
        webbrowser.open(f"https://translate.google.com/?sl=auto&tl={target_language}&text={text}")
    except Exception as e:
        speak_func("Sorry, I couldn't translate that.")

def set_reminder(reminder_text, time_minutes=5, speak_func=None):
    """Set a simple reminder"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    speak_func(f"I'll remind you about {reminder_text} in {time_minutes} minutes")
    # In a real implementation, you'd use threading to set an actual timer
    # For now, we'll just acknowledge the request

def take_screenshot(speak_func=None):
    """Take a screenshot"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        import pyautogui
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        speak_func(f"Screenshot saved as {filename}")
    except Exception as e:
        speak_func("Sorry, I couldn't take a screenshot.")

def get_system_info(speak_func=None, query=None, use_mcp=True):
    """Get comprehensive system information including CPU, memory, disk, and network"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    
    # Try MCP first if enabled
    if use_mcp:
        try:
            import asyncio
            from engine.mcp_client import mcp_client
            
            # Run async MCP call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(mcp_client.call_tool("get_system_info", {}))
            loop.close()
            
            if result:
                print("✅ Using MCP for system info")
                speak_func(result)
                return result
        except Exception as e:
            print(f"⚠️ MCP system info failed, using direct method: {e}")
    
    # Direct implementation (fallback or when MCP disabled)
    try:
        import platform
        import psutil
        
        # Get CPU usage with a short interval for more accurate reading
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        # Network information
        net_io = psutil.net_io_counters()
        bytes_sent_mb = net_io.bytes_sent / (1024**2)
        bytes_recv_mb = net_io.bytes_recv / (1024**2)
        
        # Build comprehensive response
        if query and 'cpu' in query.lower() and not any(word in query.lower() for word in ['all', 'full', 'complete', 'everything']):
            # CPU-specific query
            response = f"CPU Usage: {cpu_percent}% across {cpu_count} cores"
        elif query and 'memory' in query.lower() and not any(word in query.lower() for word in ['all', 'full', 'complete', 'everything']):
            # Memory-specific query
            response = f"Memory Usage: {memory.percent}% used. {memory_used_gb:.1f} GB out of {memory_total_gb:.1f} GB"
        elif query and 'disk' in query.lower() and not any(word in query.lower() for word in ['all', 'full', 'complete', 'everything']):
            # Disk-specific query
            response = f"Disk Usage: {disk.percent}% used. {disk_used_gb:.1f} GB out of {disk_total_gb:.1f} GB"
        elif query and 'network' in query.lower() and not any(word in query.lower() for word in ['all', 'full', 'complete', 'everything']):
            # Network-specific query
            response = f"Network: Sent {bytes_sent_mb:.1f} MB, Received {bytes_recv_mb:.1f} MB"
        else:
            # Full system information (default for "cpu usage" query)
            os_info = f"{platform.system()} {platform.release()}"
            response = (
                f"System Status: "
                f"CPU {cpu_percent}%, "
                f"Memory {memory.percent}% ({memory_used_gb:.1f}/{memory_total_gb:.1f} GB), "
                f"Disk {disk.percent}% ({disk_used_gb:.1f}/{disk_total_gb:.1f} GB), "
                f"Network sent {bytes_sent_mb:.1f} MB, received {bytes_recv_mb:.1f} MB"
            )
        
        speak_func(response)
        return response
        
    except Exception as e:
        error_msg = f"Sorry, I couldn't get system information: {str(e)}"
        speak_func(error_msg)
        return error_msg

def open_file_explorer(path="", speak_func=None):
    """Open file explorer to a specific path"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        if path:
            os.system(f'explorer "{path}"')
            speak_func(f"Opening file explorer to {path}")
        else:
            os.system('explorer')
            speak_func("Opening file explorer")
    except Exception as e:
        speak_func("Sorry, I couldn't open file explorer.")

def search_files(filename, speak_func=None):
    """Search for files on the computer"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func(f"Searching for {filename}")
        os.system(f'start ms-settings:search')
    except Exception as e:
        speak_func("Sorry, I couldn't search for files.")

def get_news(speak_func=None):
    """Get latest news"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func("Opening news website")
        webbrowser.open("https://news.google.com")
    except Exception as e:
        speak_func("Sorry, I couldn't get the news.")

def play_music(speak_func=None):
    """Open a music streaming service"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func("Opening Spotify")
        webbrowser.open("https://open.spotify.com")
    except Exception as e:
        speak_func("Sorry, I couldn't open music.")

def open_spotify_app(speak_func=None):
    """Open Spotify desktop application"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    
    try:
        # Use the improved spotify_api function
        from engine.spotify_api import open_spotify_app as open_spotify
        return open_spotify(speak_func)
        
    except Exception as e:
        speak_func("Sorry, I couldn't open Spotify.")
        return False

def play_specific_song_siri_style(song_name, speak_func=None):
    """Play a specific song on Spotify like Siri would - actually play the song"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    
    try:
        # Use the improved spotify_api functions
        from engine.spotify_api import search_and_play_song
        success = search_and_play_song(song_name, speak_func)
        return success
        
    except Exception as e:
        print(f"Spotify play error: {e}")
        # Fallback to simple web search
        try:
            import urllib.parse
            encoded_song = urllib.parse.quote(song_name)
            spotify_url = f"https://open.spotify.com/search/{encoded_song}"
            speak_func(f"Opening Spotify to search for {song_name}")
            webbrowser.open(spotify_url)
            return True
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            speak_func(f"Sorry, I couldn't play {song_name} on Spotify.")
            return False

def play_specific_song(song_name, speak_func=None):
    """Legacy function - now calls the Siri-style function"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    return play_specific_song_siri_style(song_name, speak_func)

def play_song_with_spotify_uri(song_name, speak_func=None):
    """Alternative method using Spotify URI protocol"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func(f"Playing {song_name} on Spotify using URI method")
        
        # This method tries to use Spotify's URI protocol more effectively
        import urllib.parse
        import time
        
        # Try different Spotify URI formats
        uri_methods = [
            f"spotify:search:{song_name}",
            f"spotify:search:{song_name.replace(' ', '%20')}",
            f"spotify:search:{song_name.replace(' ', '+')}"
        ]
        
        for uri in uri_methods:
            try:
                os.system(f'start "{uri}"')
                time.sleep(3)  # Give it time to process
                return True
            except:
                continue
        
        # If URI methods fail, fall back to web player with better formatting
        speak_func("Opening Spotify web player")
        
        # Use better URL encoding
        clean_song_name = song_name.replace(' ', '%20').replace('&', '%26')
        webbrowser.open(f"https://open.spotify.com/search/{clean_song_name}")
        return True
        
    except Exception as e:
        speak_func(f"Sorry, I couldn't play {song_name} using Spotify URI.")
        return False

def send_email(speak_func=None):
    """Open email client"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func("Opening Gmail")
        webbrowser.open("https://mail.google.com")
    except Exception as e:
        speak_func("Sorry, I couldn't open email.")

def get_definition(word, speak_func=None):
    """Get definition of a word"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func(f"Looking up the definition of {word}")
        webbrowser.open(f"https://www.merriam-webster.com/dictionary/{word}")
    except Exception as e:
        speak_func("Sorry, I couldn't find the definition.")

def convert_currency(amount, from_currency="USD", to_currency="EUR", speak_func=None):
    """Convert currency"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        speak_func(f"Converting {amount} {from_currency} to {to_currency}")
        webbrowser.open(f"https://www.google.com/search?q={amount}+{from_currency}+to+{to_currency}")
    except Exception as e:
        speak_func("Sorry, I couldn't convert the currency.")

def get_random_fact(speak_func=None):
    """Get a random interesting fact"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
        "A day on Venus is longer than its year. Venus takes 243 Earth days to rotate on its axis but only 225 Earth days to orbit the Sun.",
        "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after just 38 minutes.",
        "Bananas are berries, but strawberries aren't. In botanical terms, a berry is a fruit produced from the ovary of a single flower.",
        "The Great Wall of China is not visible from space with the naked eye, despite the popular myth."
    ]
    import random
    fact = random.choice(facts)
    speak_func(f"Here's a random fact: {fact}")

def get_motivational_quote(speak_func=None):
    """Get a motivational quote"""
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt"
    ]
    import random
    quote = random.choice(quotes)
    speak_func(f"Here's a motivational quote: {quote}")

def draft_email(prompt, speak_func=None):
    """Draft an email using the AI assistant (tinyllama)."""
    from engine.ai_assistant import spitch_ai
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    generative_system_prompt = "You are a helpful AI assistant that drafts professional, friendly, and clear emails based on user requests."
    try:
        ai_result = spitch_ai.process_command(prompt, system_prompt_override=generative_system_prompt, model='tinyllama')
        ai_response = ai_result.get("response")
        if ai_response:
            speak_func(ai_response)
        else:
            speak_func("I'm sorry, I couldn't generate an email draft for that request.")
    except Exception as e:
        print(f"AI processing error for email draft: {e}")
        speak_func("I'm having trouble connecting to my AI services to draft that email.")

def draft_whatsapp_message(prompt, speak_func=None):
    """Draft a WhatsApp message using the AI assistant (tinyllama)."""
    from engine.ai_assistant import spitch_ai
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    generative_system_prompt = "You are a helpful AI assistant that drafts friendly, concise WhatsApp messages based on user requests."
    try:
        ai_result = spitch_ai.process_command(prompt, system_prompt_override=generative_system_prompt, model='tinyllama')
        ai_response = ai_result.get("response")
        if ai_response:
            speak_func(ai_response)
        else:
            speak_func("I'm sorry, I couldn't generate a WhatsApp message for that request.")
    except Exception as e:
        print(f"AI processing error for WhatsApp draft: {e}")
        speak_func("I'm having trouble connecting to my AI services to draft that WhatsApp message.")

def send_whatsapp_message_via_web(phone_number, message, speak_func=None):
    """Open WhatsApp Web to send a message to a specific phone number with a pre-filled message."""
    import urllib.parse
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    try:
        encoded_message = urllib.parse.quote(message)
        url = f"https://wa.me/{phone_number}?text={encoded_message}"
        speak_func(f"Opening WhatsApp Web to send your message. Please press send in your browser.")
        webbrowser.open(url)
    except Exception as e:
        print(f"WhatsApp Web send error: {e}")
        speak_func("Sorry, I couldn't open WhatsApp Web to send your message.") 