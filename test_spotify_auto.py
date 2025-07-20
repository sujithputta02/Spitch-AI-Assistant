#!/usr/bin/env python3
"""
Test script for improved Spotify auto-play functionality
"""

def test_spotify_auto_play():
    """Test the improved Spotify integration with automatic device handling"""
    print("🎵 Testing Improved Spotify Auto-Play")
    print("=" * 50)
    
    try:
        from engine.spotify_api import search_and_play_song
        
        def mock_speak(text):
            print(f"  Assistant: {text}")
        
        # Test with the song that was causing issues
        test_song = "theme of kalki"
        print(f"\nTesting: '{test_song}'")
        print("-" * 30)
        
        result = search_and_play_song(test_song, speak_func=mock_speak)
        print(f"\nFinal Result: {'Success' if result else 'Fallback to web player'}")
        
        print("\n💡 What this does:")
        print("   1. Tries to play the song directly via Spotipy")
        print("   2. If no active device found, opens Spotify app automatically")
        print("   3. Waits 3 seconds for app to start")
        print("   4. Tries playing again")
        print("   5. If still fails, opens web player as fallback")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_spotify_auto_play() 