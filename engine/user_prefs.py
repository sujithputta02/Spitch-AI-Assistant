import json
import os

SETTINGS_FILE = 'user_settings.json'

def save_setting(key: str, value):
    """Saves a key-value pair to the settings file."""
    settings = load_settings()
    settings[key] = value
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving settings: {e}")
        return False

def load_setting(key: str, default=None):
    """Loads a specific key from the settings file."""
    settings = load_settings()
    return settings.get(key, default)

def load_settings() -> dict:
    """Loads the entire settings dictionary from the file."""
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

def set_user_location(city: str, speak_func=None):
    """Saves the user's preferred location."""
    if save_setting('user_location', city):
        if speak_func:
            speak_func(f"I've set your default location to {city}.")
        return True
    else:
        if speak_func:
            speak_func("I'm sorry, I couldn't save your location setting.")
        return False

def get_user_location():
    """Retrieves the user's saved location."""
    return load_setting('user_location') 