import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.user_prefs import set_user_location, get_user_location
from engine.weather import get_weather

def mock_speak(text):
    """A simple function to print what the assistant would say."""
    print(f"ASSISTANT: {text}")

def test_manual_location():
    """Tests the full manual location workflow."""
    settings_file = 'user_settings.json'
    
    # --- Clean up any previous settings file for a clean test ---
    if os.path.exists(settings_file):
        os.remove(settings_file)
        print("--- Cleared previous user settings ---")

    print("\n--- 1. Testing weather with NO location set (should use IP) ---")
    get_weather(query="weather in my location", speak_func=mock_speak)
    
    print("\n--- 2. Setting a manual location ---")
    manual_city = "Hyderabad"
    print(f"COMMAND: Set my location to {manual_city}")
    set_user_location(manual_city, speak_func=mock_speak)
    
    # Verify it was saved
    saved_city = get_user_location()
    print(f"VERIFICATION: Saved location is '{saved_city}'")
    assert saved_city == manual_city, "Location was not saved correctly!"
    
    print("\n--- 3. Testing weather again WITH manual location set ---")
    get_weather(query="weather in my current location", speak_func=mock_speak)

    print("\n--- Test Complete ---")
    
    # --- Final cleanup ---
    if os.path.exists(settings_file):
        os.remove(settings_file)

if __name__ == "__main__":
    test_manual_location() 