#!/usr/bin/env python3
"""
Demonstration of Spotify voice commands
"""

def demo_spotify_commands():
    """Demonstrate Spotify voice commands"""
    print("🎵 Spotify Voice Commands Demo")
    print("=" * 40)
    
    # Test commands
    test_commands = [
        "play cornfield chase from spotify",
        "play chinni chinni asha from spotify",
        "play despacito from spotify",
        "play shape of you from spotify",
        "play music from spotify",
        "open spotify app"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Testing: '{command}'")
        print("-" * 30)
        
        # Test the command processing logic without Eel
        query_lower = command.lower().strip()
        
        if 'play' in query_lower and ('youtube' in query_lower or 'spotify' in query_lower or 'music' in query_lower):
            # Extract song name from Spotify request
            song_name = query_lower
            # Remove common words
            song_name = song_name.replace('play', '').replace('from spotify', '').replace('spotify', '').replace('app', '').replace('music', '').strip()
            # Clean up extra spaces
            song_name = ' '.join(song_name.split())
            
            print(f"Extracted song name: '{song_name}'")
            
            if song_name:
                print(f"✅ Would play: {song_name} on Spotify")
                print("   This would open Spotify web player with search results")
            else:
                print("❌ No song name extracted")
        elif 'open spotify' in query_lower:
            print("✅ Would open Spotify desktop app")
        else:
            print("❌ Command not recognized")
        
        # Wait a bit between commands
        import time
        time.sleep(1)
    
    print("\n🎉 Demo completed!")
    print("\n💡 Try these voice commands with Sophia:")
    print("   • 'Play cornfield chase from spotify'")
    print("   • 'Play despacito from spotify'")
    print("   • 'Open spotify app'")
    print("   • 'Play music from spotify'")
    print("\n🔧 How it works:")
    print("   1. Sophia extracts the song name from your voice command")
    print("   2. Opens Spotify web player with search results")
    print("   3. You can click to play the song")
    print("   4. Or use the desktop app if available")

if __name__ == "__main__":
    demo_spotify_commands() 