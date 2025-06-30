#!/usr/bin/env python3
"""
Final test for Spotify integration through command processing
"""

from engine.command import process_direct_command
from engine.speak_utils import speak

def test_spotify_commands():
    """Test Spotify commands through the main command processing system"""
    print("🎵 Testing Spotify Commands Through Main System")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        "play cornfield chase from spotify",
        "play chinni chinni asha from spotify",
        "play despacito from spotify",
        "play shape of you from spotify",
        "open spotify app"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Testing: '{command}'")
        print("-" * 40)
        
        # Process through main command system
        result = process_direct_command(command)
        print(f"Result: {result}")
        
        # Small delay between tests
        import time
        time.sleep(1)
    
    print("\n✅ Spotify integration test completed!")

if __name__ == "__main__":
    test_spotify_commands() 