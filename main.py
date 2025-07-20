import sys
import inspect
if sys.version_info >= (3, 11):
    if not hasattr(inspect, 'getargspec'):
        def getargspec(func):
            from inspect import getfullargspec, ArgSpec
            spec = getfullargspec(func)
            return ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)
        inspect.getargspec = getargspec

import os
import eel
import threading
import time
import re
import speech_recognition as sr
from engine.features import *
from engine.command import *
from engine.speak_utils import speak

eel.init('www')

# Global variable to control continuous listening
continuous_listening = False
listening_thread = None
wake_word_enabled = False  # Disable wake word by default for easier use

def continuous_listen():
    """Background thread function for continuous voice listening"""
    global continuous_listening
    while continuous_listening:
        try:
            print("🔊 Listening for voice commands...")
            eel.DisplayMessage("Listening... Say 'stop' or 'goodbye' to stop me")
            
            # Take a voice command
            query = takeCommand()
            
            if query:
                print(f"🎤 Heard: {query}")
                
                # Check for stop command first
                if any(phrase in query.lower() for phrase in ['stop', 'stop listening', 'stop assistant', 'goodbye', 'exit', 'quit', 'bye', 'end']):
                    speak("Stopping voice assistant. Goodbye!")
                    stop_continuous_listening()
                    eel.force_stop_listening_ui()
                    break
                
                # Process the command directly (no wake word required)
                print(f"🎯 Processing command: {query}")
                processTextCommand(query)
                
                # Brief pause before listening again
                time.sleep(1)
            else:
                # No speech detected, continue listening
                time.sleep(0.5)
                
        except sr.WaitTimeoutError:
            # Speech recognition timeout - this is normal, just continue
            print("Listening timeout - continuing...")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error in continuous listening: {e}")
            time.sleep(1)

@eel.expose
def start_continuous_listening():
    """Start continuous voice listening mode (called when mic button is clicked)"""
    global continuous_listening, listening_thread
    
    if not continuous_listening:
        continuous_listening = True
        speak("Voice assistant activated. I'm listening for your commands. Say 'stop' to stop me.")
        
        # Start listening in background thread
        listening_thread = threading.Thread(target=continuous_listen, daemon=True)
        listening_thread.start()
        
        return {"status": "started", "message": "Voice assistant started"}
    else:
        return {"status": "already_running", "message": "Voice assistant already running"}

@eel.expose
def stop_continuous_listening():
    """Stop continuous voice listening mode"""
    global continuous_listening, listening_thread
    
    if continuous_listening:
        continuous_listening = False
        
        # Don't try to join the current thread
        if listening_thread and listening_thread.is_alive() and listening_thread != threading.current_thread():
            try:
                listening_thread.join(timeout=2)
            except Exception as e:
                print(f"Thread join error (non-critical): {e}")
        
        speak("Voice assistant stopped.")
        return {"status": "stopped", "message": "Voice assistant stopped"}
    else:
        return {"status": "not_running", "message": "Voice assistant not running"}

@eel.expose
def get_listening_status():
    """Get current listening status"""
    global continuous_listening
    return {"listening": continuous_listening}

@eel.expose
def toggle_wake_word():
    """Toggle wake word detection on/off"""
    global wake_word_enabled
    wake_word_enabled = not wake_word_enabled
    status = "enabled" if wake_word_enabled else "disabled"
    speak(f"Wake word detection {status}.")
    return {"wake_word_enabled": wake_word_enabled, "status": status}

# Welcome message
playAssistantSound()
speak("Hello! I'm Spitch, your AI assistant. Click the microphone button to start voice commands, or type your commands in the text box. I can help you with music, apps, web searches, and much more!")

# Open the web interface (handled by Eel now)
# os.system('start chrome.exe --app="http://localhost:8000/index.html"')

if __name__ == "__main__":
    try:
        # Start Eel with landing page
        eel.start('landing.html', mode='chrome', host='localhost', block=True)
    except EnvironmentError:
        print("Chrome not found. Opening in default browser.")
        eel.start('landing.html', mode='default', host='localhost', block=True)