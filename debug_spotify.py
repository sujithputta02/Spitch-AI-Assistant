#!/usr/bin/env python3
"""
Debug script for Spotify functionality
"""

import os
import time
import webbrowser
import urllib.parse

def debug_spotify_command(query):
    """Debug the Spotify command processing step by step"""
    
    print(f"Debugging command: '{query}'")
    print("=" * 50)
    
    # Step 1: Extract song name
    song_name = query.lower()
    song_name = song_name.replace('play', '').replace('from spotify', '').replace('spotify', '').replace('app', '').replace('music', '').strip()
    song_name = ' '.join(song_name.split())
    
    print(f"Step 1 - Extracted song name: '{song_name}'")
    
    if not song_name:
        print("❌ No song name extracted!")
        return False
    
    # Step 2: Test Spotify URI method
    print(f"\nStep 2 - Testing Spotify URI method for '{song_name}'")
    try:
        encoded_song = urllib.parse.quote(song_name)
        uri = f"spotify:search:{encoded_song}"
        print(f"  URI: {uri}")
        
        # Test if we can execute the command
        print("  Executing: os.system(f'start \"{uri}\"')")
        result = os.system(f'start "{uri}"')
        print(f"  Result code: {result}")
        
        if result == 0:
            print("  ✅ URI method executed successfully")
        else:
            print("  ❌ URI method failed")
            
    except Exception as e:
        print(f"  ❌ URI method error: {e}")
    
    # Step 3: Test web player method
    print(f"\nStep 3 - Testing web player method for '{song_name}'")
    try:
        clean_song_name = urllib.parse.quote(song_name)
        web_url = f"https://open.spotify.com/search/{clean_song_name}"
        print(f"  Web URL: {web_url}")
        
        print("  Opening web player...")
        webbrowser.open(web_url)
        print("  ✅ Web player opened")
        
    except Exception as e:
        print(f"  ❌ Web player error: {e}")
    
    # Step 4: Test if Spotify is installed
    print(f"\nStep 4 - Checking Spotify installation")
    try:
        # Check common Spotify paths
        spotify_paths = [
            os.path.expanduser("~/AppData/Roaming/Spotify/Spotify.exe"),
            "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe",
            "C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_*\\Spotify.exe",
            "C:\\Program Files (x86)\\Spotify\\Spotify.exe"
        ]
        
        for path in spotify_paths:
            if os.path.exists(path):
                print(f"  ✅ Found Spotify at: {path}")
                break
        else:
            print("  ❌ Spotify not found in common locations")
            
    except Exception as e:
        print(f"  ❌ Error checking Spotify: {e}")
    
    print("\n" + "=" * 50)
    print("Debug completed!")
    return True

if __name__ == "__main__":
    # Test with the exact command from the user
    test_commands = [
        "play chinni chinni asha from spotify app",
        "chinni chinni asha from spotify app",
        "play cornfield chase from spotify"
    ]
    
    for command in test_commands:
        debug_spotify_command(command)
        print("\n" + "-" * 50 + "\n") 