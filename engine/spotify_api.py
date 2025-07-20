import webbrowser
import urllib.parse
import os
import subprocess
import time
import re

# Spotipy integration
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from engine.ai_assistant import spitch_ai

CLIENT_ID = '65b0dda2962c4b8db17ddc41c9825149'
CLIENT_SECRET = 'ad5e1281cfd24401b668b67a4ac4231a'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'

SPOTIFY_SCOPE = (
    'user-modify-playback-state user-read-playback-state user-read-currently-playing '
    'playlist-modify-public playlist-modify-private user-top-read user-read-recently-played'
)

def _get_spotify_client():
    """Returns an authenticated Spotipy client."""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    ))

def spotipy_play_song(song_name, speak_func=None):
    try:
        sp = _get_spotify_client()
        results = sp.search(q=song_name, type='track', limit=10)
        tracks = results['tracks']['items']
        if not tracks:
            if speak_func:
                speak_func(f"No track found for {song_name} on Spotify.")
            return False

        # --- Advanced Song Selection Logic ---
        best_match = None
        song_name_lower = song_name.lower()

        # Prioritize tracks that contain all keywords and "ost" or "soundtrack"
        for track in tracks:
            track_name_lower = track['name'].lower()
            if all(word in track_name_lower for word in song_name_lower.split()) and \
               ('ost' in track_name_lower or 'soundtrack' in track_name_lower):
                best_match = track
                break 

        # Fallback: find a track that contains the song name
        if not best_match:
            for track in tracks:
                if song_name_lower in track['name'].lower():
                    best_match = track
                    break
        
        # Fallback: if no good match is found, take the first result
        if not best_match:
            best_match = tracks[0]

        track_uri = best_match['uri']
        track_name = best_match['name']
        artist_name = best_match['artists'][0]['name']
        if speak_func:
            speak_func(f"Playing {track_name} by {artist_name} on Spotify.")
        
        try:
            sp.start_playback(uris=[track_uri])
            return True
        except Exception as playback_error:
            if "NO_ACTIVE_DEVICE" in str(playback_error) or "No active device found" in str(playback_error):
                # Try to find and activate a device
                devices = sp.devices().get('devices', [])
                if not devices:
                    if speak_func:
                        speak_func("No Spotify devices found. Please open the Spotify app on your device and try again.")
                    open_spotify_app(speak_func=None)
                    return False
                # Try to transfer playback to the first available device
                device_id = devices[0]['id']
                device_name = devices[0]['name']
                if speak_func:
                    speak_func(f"Transferring playback to {device_name} and trying again...")
                sp.transfer_playback(device_id, force_play=True)
                time.sleep(2)
                try:
                    sp.start_playback(uris=[track_uri], device_id=device_id)
                    if speak_func:
                        speak_func(f"Now playing {track_name} by {artist_name} on {device_name}.")
                    return True
                except Exception as retry_error:
                    if speak_func:
                        speak_func("Still couldn't auto-play. Please check your Spotify app and try again.")
                    return False
            else:
                raise playback_error
    except Exception as e:
        print(f"Spotipy error: {e}")
        if speak_func:
            speak_func("Sorry, I couldn't auto-play the song on Spotify. Please make sure Spotify is open and you have an active device selected.")
        return False

def search_and_play_song(song_name, speak_func=None, allow_web_fallback=False):
    """Search for a song and open it in Spotify using Spotipy if possible, else fallback to web if allowed"""
    # Try Spotipy auto-play first
    if spotipy_play_song(song_name, speak_func):
        return True
    # Fallback to web search only if allowed
    if allow_web_fallback:
        try:
            if speak_func:
                speak_func(f"Opening Spotify web player to search for {song_name}")
            encoded_song = urllib.parse.quote(song_name)
            spotify_url = f"https://open.spotify.com/search/{encoded_song}"
            webbrowser.open(spotify_url)
            return True
        except Exception as e:
            print(f"Spotify web player error: {e}")
            if speak_func:
                speak_func("Sorry, I couldn't open Spotify.")
            return False
    return False

def open_spotify_app(speak_func=None):
    """Open Spotify desktop application"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(["start", "spotify:"], shell=True)
        else:
            subprocess.Popen(["spotify"])
        if speak_func:
            speak_func("Opening Spotify app.")
        return True
    except Exception as e:
        print(f"Error opening Spotify app: {e}")
        if speak_func:
            speak_func("Sorry, I couldn't open Spotify app.")
        return False

def pause_music(speak_func=None):
    """Pause the currently playing music on Spotify."""
    try:
        sp = _get_spotify_client()
        devices = sp.devices().get('devices', [])
        if not devices:
            if speak_func:
                speak_func("No active Spotify device found. Please open Spotify and play something.")
            return False
        sp.pause_playback()
        if speak_func:
            speak_func("Music paused.")
        return True
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 403 and "Restriction violated" in e.msg:
            if speak_func:
                speak_func("I couldn't do that. This feature might require a Spotify Premium account.")
        else:
            if speak_func:
                speak_func("I couldn't pause the music. Please make sure Spotify is active.")
        print(f"Spotify API error: {e}")
        return False
    except Exception as e:
        print(f"Error pausing music: {e}")
        if speak_func:
            speak_func("An unexpected error occurred while trying to pause the music.")
        return False

def resume_music(speak_func=None):
    """Resume the currently paused music on Spotify."""
    try:
        sp = _get_spotify_client()
        devices = sp.devices().get('devices', [])
        if not devices:
            if speak_func:
                speak_func("No active Spotify device found. Please open Spotify and play something.")
            return False
        sp.start_playback()
        if speak_func:
            speak_func("Resuming music.")
        return True
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 403 and "Restriction violated" in e.msg:
            if speak_func:
                speak_func("I couldn't do that. This feature might require a Spotify Premium account.")
        else:
            if speak_func:
                speak_func("I couldn't resume the music. Please make sure Spotify is active.")
        print(f"Spotify API error: {e}")
        return False
    except Exception as e:
        print(f"Error resuming music: {e}")
        if speak_func:
            speak_func("An unexpected error occurred while trying to resume the music.")
        return False

def handle_spotify_inquiry(query, speak_func):
    """Handles advanced Spotify-related inquiries."""
    try:
        sp = _get_spotify_client()
        query_lower = query.lower()

        # Music Discovery
        if "play music similar to" in query_lower:
            topic = query_lower.replace("play music similar to", "").strip()
            speak_func(f"Finding music similar to {topic}...")
            # Simple implementation: search for the topic as a playlist and play it
            playlists = sp.search(q=topic, type='playlist', limit=1)
            if playlists['playlists']['items']:
                playlist_uri = playlists['playlists']['items'][0]['uri']
                sp.start_playback(context_uri=playlist_uri)
            else:
                speak_func(f"Sorry, I couldn't find a playlist for {topic}.")
            return

        if "trending songs" in query_lower:
            # Simplistic approach: Play a "Top Hits" playlist for the region if specified
            # A true "trending" feature is complex, so we use a proxy.
            speak_func("Finding a trending playlist for you...")
            playlists = sp.search(q="Top 50", type='playlist', limit=1)
            if playlists['playlists']['items']:
                playlist_uri = playlists['playlists']['items'][0]['uri']
                sp.start_playback(context_uri=playlist_uri)
            else:
                speak_func("I couldn't find a trending playlist.")
            return
            
        if "top 10 songs" in query_lower or "top songs on spotify" in query_lower:
            speak_func("Here are the top songs on Spotify right now, based on the Global Top 50 playlist.")
            playlists = sp.search(q="Top 50 Global", type='playlist', limit=1)
            if playlists['playlists']['items']:
                playlist_uri = playlists['playlists']['items'][0]['uri']
                sp.start_playback(context_uri=playlist_uri)
            else:
                speak_func("I couldn't find the Global Top 50 playlist.")
            return

        # Playlist Management
        if "create a playlist called" in query_lower:
            name_part = query_lower.split("called")[-1].strip()
            playlist_name = name_part.split("with songs by")[0].strip()
            user_id = sp.me()['id']
            sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
            speak_func(f"I've created a new playlist called {playlist_name}.")
            return

        if "add this song to" in query_lower:
            playlist_name = query_lower.split("my")[-1].replace("playlist", "").strip()
            current_track = sp.current_playback()
            if current_track and current_track['item']:
                track_uri = current_track['item']['uri']
                playlists = sp.current_user_playlists()
                target_playlist = next((p for p in playlists['items'] if p['name'].lower() == playlist_name.lower()), None)
                if target_playlist:
                    sp.playlist_add_items(target_playlist['id'], [track_uri])
                    speak_func(f"Added the current song to your {playlist_name} playlist.")
                else:
                    speak_func(f"I couldn't find a playlist named {playlist_name}.")
            else:
                speak_func("You need to be playing a song to add it to a playlist.")
            return

        # Personalization & Daily Use
        if "discover weekly" in query_lower:
            speak_func("Looking for your Discover Weekly playlist...")
            playlists_result = sp.search(q="Discover Weekly", type='playlist', limit=10)
            
            # Safely check if the search returned any playlists
            if not playlists_result or not playlists_result.get('playlists') or not playlists_result['playlists'].get('items'):
                speak_func("I couldn't find any playlists named Discover Weekly.")
                return

            dw_playlist = None
            for p in playlists_result['playlists']['items']:
                # Check for owner and name safely to avoid errors
                owner = p.get('owner')
                if owner and owner.get('display_name') == 'Spotify' and 'discover weekly' in p.get('name', '').lower():
                    dw_playlist = p
                    break  # Found it

            if dw_playlist:
                sp.start_playback(context_uri=dw_playlist['uri'])
                speak_func("Playing your Discover Weekly playlist.")
            else:
                speak_func("I couldn't find your Discover Weekly playlist. Please make sure it's in your library.")
            return

        if "most played song" in query_lower:
            top_tracks = sp.current_user_top_tracks(limit=1, time_range='short_term')
            if top_tracks and top_tracks.get('items'):
                song_name = top_tracks['items'][0]['name']
                speak_func(f"Your most played song recently is {song_name}.")
            else:
                speak_func("I couldn't determine your most played song.")
            return

        # Podcast Support
        if "podcast" in query_lower or "episode" in query_lower:
            # Try to extract podcast name or genre
            match = re.search(r"(?:play|find|latest episode of|podcast)(.*?)(?:on spotify|with high ratings|$)", query_lower)
            podcast_query = match.group(1).strip() if match else ""
            if not podcast_query:
                podcast_query = query_lower.replace("play","").replace("find","").replace("podcast","").replace("on spotify","").replace("latest episode of","").replace("with high ratings","").strip()
            if not podcast_query:
                speak_func("Please specify the podcast or genre you want.")
                return
            speak_func(f"Searching for podcasts about {podcast_query} on Spotify...")
            # Search for podcasts (shows) matching the query
            shows = sp.search(q=podcast_query, type='show', limit=3)
            if shows and shows.get('shows') and shows['shows'].get('items'):
                show = shows['shows']['items'][0]
                show_name = show['name']
                show_uri = show['uri']
                # Get episodes for the show
                episodes = sp.show_episodes(show['id'], limit=1)
                if episodes and episodes.get('items'):
                    episode = episodes['items'][0]
                    episode_name = episode['name']
                    episode_uri = episode['uri']
                    sp.start_playback(uris=[episode_uri])
                    speak_func(f"Playing the latest episode of {show_name}: {episode_name}.")
                    return
                else:
                    sp.start_playback(context_uri=show_uri)
                    speak_func(f"Playing podcast {show_name}.")
                    return
            else:
                speak_func(f"Sorry, I couldn't find a podcast matching '{podcast_query}' on Spotify.")
            return

        # Fallback to AI for more complex queries
        prompt = f"As a Spotify expert, provide a helpful, conversational response for the following request: '{query}'"
        generative_system_prompt = "You are a helpful and creative AI assistant specializing in Spotify. Provide a detailed and insightful response to the user's request. Do not output JSON."
        ai_result = spitch_ai.process_command(query, system_prompt_override=generative_system_prompt, model='tinyllama')
        ai_response = ai_result.get("response") if ai_result else None
        if ai_response:
            speak_func(ai_response)
        else:
            speak_func("I'm not sure how to handle that Spotify request. You can ask me to play songs, create playlists, or find trending music.")

    except Exception as e:
        print(f"Spotify inquiry error: {e}")
        speak_func("I'm having trouble with that Spotify request. Please make sure your Spotify app is open and you're logged in.") 