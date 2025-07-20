#!/usr/bin/env python3
"""
Test script for Siri-style Spotify functionality
"""

def test_siri_spotify():
    """Test the Siri-style Spotify song playing"""
    
    # Import the function
    from engine.advanced_features import play_specific_song_siri_style
    
    # Test song names
    test_songs = [
        "cornfield chase",
        "chinni chinni asha",
        "shape of you",
        "despacito"
    ]
    
    print("Testing Siri-style Spotify functionality...")
    print("This will attempt to play songs like Siri would.")
    print("Note: This is a test - actual playing depends on Spotify installation and permissions.\n")
    
    for song in test_songs:
        print(f"Testing: '{song}'")
        try:
            # Create a mock speak function for testing
            def mock_speak(text):
                print(f"  Assistant says: {text}")
            
            # Test the function
            result = play_specific_song_siri_style(song, speak_func=mock_speak)
            print(f"  Result: {'Success' if result else 'Failed'}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        print()

if __name__ == "__main__":
    test_siri_spotify()
    print("Test completed!") 