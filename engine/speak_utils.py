import pyttsx3
import eel
from engine.user_prefs import load_setting

def speak(text):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # Load settings
        voice_id_pref = load_setting('voice_id')
        voice_rate_pref = load_setting('voice_rate', 170)
        
        # Select voice
        if voice_id_pref:
            engine.setProperty('voice', voice_id_pref)
        else:
            # Default fallback
            engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            
        engine.setProperty('rate', int(voice_rate_pref))
        
        try:
            eel.DisplayMessage(text)  # Show text in UI if available
        except (AttributeError, Exception):
            print(f"[Spitch] {text}")  # Fallback to console output
            
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Text-to-speech error: {e}")

@eel.expose
def get_voice_options():
    """Return list of available voices for the UI"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_list = []
        for v in voices:
            voice_list.append({
                'id': v.id,
                'name': v.name,
                'lang': v.languages
            })
        return voice_list
    except Exception as e:
        print(f"Error getting voices: {e}")
        return [] 