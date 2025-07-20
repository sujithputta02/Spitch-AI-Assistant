#!/usr/bin/env python3
"""
Test script to verify Spotify integration fixes
"""

def test_spotify_integration():
    """Test the Spotify integration to ensure webbrowser scope issue is fixed"""
    print("🧪 Testing Spotify Integration Fixes")
    print("=" * 50)
    
    # Test 1: Import the functions
    try:
        from engine.features import PlayYoutube
        from engine.spotify_api import search_and_play_song
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Test Spotify song extraction
    test_commands = [
        "play cornfield chase from spotify",
        "play chinni chinni asha from spotify app",
        "play despacito from spotify"
    ]
    
    for command in test_commands:
        print(f"\nTesting command: '{command}'")
        try:
            # This should not throw a webbrowser scope error
            PlayYoutube(command)
            print("✅ Command processed without webbrowser error")
        except Exception as e:
            print(f"❌ Error processing command: {e}")
            if "webbrowser" in str(e).lower():
                print("   This indicates the webbrowser scope issue is not fixed")
                return False
    
    # Test 3: Test direct Spotify API
    print(f"\nTesting direct Spotify API...")
    try:
        def mock_speak(text):
            print(f"  Assistant says: {text}")
        
        result = search_and_play_song("test song", speak_func=mock_speak)
        print(f"✅ Spotify API test completed (result: {result})")
    except Exception as e:
        print(f"❌ Spotify API error: {e}")
    
    print("\n🎉 All tests completed!")
    print("\n💡 The webbrowser scope issue should now be fixed.")
    print("   Try running Sophia again and test Spotify commands.")
    
    return True

if __name__ == "__main__":
    test_spotify_integration() 