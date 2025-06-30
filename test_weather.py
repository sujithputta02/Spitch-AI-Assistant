import sys
import os

# Add the project root to the Python path to allow imports from the engine module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.weather import get_weather

def mock_speak(text):
    """A simple function to print what the assistant would say."""
    print(f"ASSISTANT: {text}")

def test_current_location_weather():
    """Tests the weather function's ability to detect the user's current location."""
    print("--- Testing Weather for Current Location ---")
    
    # This query should trigger the IP-based geolocation
    query = "what is the weather in my current location"
    
    print(f"USER QUERY: \"{query}\"")
    
    # Call the function and let it print the results via the mock_speak function
    get_weather(query=query, speak_func=mock_speak)
    
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_current_location_weather() 