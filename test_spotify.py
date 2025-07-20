#!/usr/bin/env python3
"""
Test script for Spotify integration
"""

from engine.spotify_api import search_and_play_song, open_spotify_app
from engine.speak_utils import speak

def test_spotify_integration():
    """Test the Spotify integration functions"""
    print("Testing Spotify integration...")
    
    # Test 1: Open Spotify app
    print("\n1. Testing open_spotify_app...")
    result = open_spotify_app(speak_func=print)
    print(f"Result: {result}")
    
    # Test 2: Search and play a song
    print("\n2. Testing search_and_play_song...")
    test_song = "cornfield chase"
    result = search_and_play_song(test_song, speak_func=print)
    print(f"Result: {result}")
    
    # Test 3: Test with another song
    print("\n3. Testing with another song...")
    test_song2 = "chinni chinni asha"
    result = search_and_play_song(test_song2, speak_func=print)
    print(f"Result: {result}")
    
    print("\nSpotify integration test completed!")

if __name__ == "__main__":
    test_spotify_integration() 