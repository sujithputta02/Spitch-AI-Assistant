#!/usr/bin/env python3
"""
Test script for improved Spotify functionality
"""

def test_spotify_commands():
    """Test the improved Spotify command processing"""
    
    # Import the functions
    from engine.command import processTextCommand
    from engine.advanced_features import play_specific_song_siri_style
    
    # Test commands
    test_commands = [
        "play chinni chinni asha from spotify app",
        "chinni chinni asha from spotify app", 
        "play cornfield chase from spotify",
        "play despacito from spotify app"
    ]
    
    print("Testing improved Spotify functionality...")
    print("This will test both command processing and song playing.")
    print("Note: This is a test - actual playing depends on Spotify installation.\n")
    
    for command in test_commands:
        print(f"Testing command: '{command}'")
        print("-" * 50)
        
        try:
            # Test the command processing
            print("1. Testing command processing...")
            processTextCommand(command)
            print("✅ Command processing completed")
            
        except Exception as e:
            print(f"❌ Command processing error: {e}")
        
        print()
    
    # Test direct song playing
    print("Testing direct song playing...")
    test_songs = ["chinni chinni asha", "cornfield chase"]
    
    for song in test_songs:
        print(f"Testing direct play: '{song}'")
        try:
            def mock_speak(text):
                print(f"  Assistant says: {text}")
            
            result = play_specific_song_siri_style(song, speak_func=mock_speak)
            print(f"  Result: {'Success' if result else 'Failed'}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        print()

if __name__ == "__main__":
    test_spotify_commands()
    print("Test completed!") 