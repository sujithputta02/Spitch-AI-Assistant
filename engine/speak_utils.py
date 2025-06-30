import pyttsx3
import eel

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Use default English voice
    selected_voice = voices[1].id if len(voices) > 1 else voices[0].id
    engine.setProperty('voice', selected_voice)
    engine.setProperty('rate', 170)
    try:
        eel.DisplayMessage(text)  # Show text in UI if available
    except (AttributeError, Exception):
        print(f"[Spitch] {text}")  # Fallback to console output
    engine.say(text)
    engine.runAndWait() 