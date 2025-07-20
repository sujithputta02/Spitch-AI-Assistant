import requests
import re
from datetime import datetime, timedelta
from engine.user_prefs import get_user_location

GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_description(code: int) -> str:
    """Converts WMO weather code to a human-readable description."""
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "unknown weather conditions")

def get_weather(city: str = None, speak_func=None, query: str = "", forecast_days: int = 1) -> str:
    """
    Fetches the current and forecasted weather for a given city.
    - Prioritizes manually set user location.
    - Detects user's location via IP if no city is set and query implies it.
    - Provides a forecast for the specified number of days.
    """
    if not city:
        # Check for keywords indicating the user wants weather for their current location
        if any(phrase in query for phrase in ["present location", "current location", "my location", "here"]):
            # First, try to get the user's saved location
            saved_location = get_user_location()
            if saved_location:
                print(f"[Weather] Using saved location: {saved_location}")
                city = saved_location
            else:
                # Fallback to IP-based geolocation
                try:
                    print("[Weather] No saved location. Detecting via IP address...")
                    ip_info_response = requests.get('https://ipinfo.io/json', timeout=5)
                    ip_info_response.raise_for_status()
                    city = ip_info_response.json().get('city')
                    if not city:
                        raise ValueError("City not found in IP info.")
                    print(f"[Weather] Detected city via IP: {city}")
                except (requests.exceptions.RequestException, ValueError) as e:
                    print(f"[Weather] IP geolocation failed: {e}")
                    if speak_func:
                        speak_func("I can't seem to find your location. You can set it by saying, 'Set my location to...'")
                    return "IP geolocation failed."
        else:
            # Extract city from query string
            match = re.search(r"in (\w+)", query)
            if match:
                city = match.group(1).capitalize()
            else:
                if speak_func:
                    speak_func("Which city's weather would you like to know?")
                return "Please specify a city."

    # Step 1: Geocoding
    try:
        geo_response = requests.get(GEOCODING_API_URL, params={"name": city, "count": 1})
        geo_response.raise_for_status()
        geo_data = geo_response.json().get("results")
        if not geo_data:
            raise ValueError(f"Location for {city} not found.")
        location = geo_data[0]
        latitude, longitude, name = location["latitude"], location["longitude"], location.get("name", city)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"[Weather] Geocoding error: {e}")
        if speak_func:
            speak_func(f"Sorry, I couldn't find the location for {city}.")
        return "Geocoding failed."

    # Step 2: Get Weather Forecast
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": min(forecast_days, 16) # API supports up to 16 days
    }
    try:
        weather_response = requests.get(WEATHER_API_URL, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Build the weather report string
        report = ""
        
        # Current weather - More explicit and clear
        current = weather_data.get("current_weather")
        if current:
            temp = current.get('temperature')
            desc = get_weather_description(current.get('weathercode'))
            windspeed = current.get('windspeed')
            report += f"Right now in {name}, it is {temp} degrees Celsius and {desc}, with wind speeds of {windspeed} kilometers per hour. "

        # Daily forecast
        daily = weather_data.get("daily")
        if daily:
            if forecast_days == 1:
                # Make the forecast report clearer
                report += f"Today's forecast calls for {get_weather_description(daily['weathercode'][0])}, with an expected high of {daily['temperature_2m_max'][0]}° and a low of {daily['temperature_2m_min'][0]}°."
            else:
                report += f"Here is the {len(daily['time'])-1} day forecast: "
                for i, date_str in enumerate(daily["time"]):
                    # Skip today's forecast if we already gave current conditions
                    if i == 0: continue
                    day = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
                    desc = get_weather_description(daily['weathercode'][i])
                    max_temp = daily['temperature_2m_max'][i]
                    min_temp = daily['temperature_2m_min'][i]
                    report += f"On {day}, expect {desc}, with a high of {max_temp}° and a low of {min_temp}°. "
        
        if not report:
            return "Sorry, I couldn't fetch any weather information."

        if speak_func:
            speak_func(report)
        return report

    except requests.exceptions.RequestException as e:
        print(f"[Weather] Weather API error: {e}")
        if speak_func:
            speak_func("Sorry, I'm having trouble connecting to the weather service.")
        return "Weather API request failed."

def handle_weather_inquiry(query, speak_func=None):
    """Handles creative or advanced weather-related prompts using tinyllama."""
    from engine.ai_assistant import spitch_ai
    if speak_func is None:
        from engine.speak_utils import speak
        speak_func = speak
    generative_system_prompt = "You are a helpful and creative AI assistant specializing in weather and lifestyle advice. Provide a detailed, actionable, and creative response for the following weather-related request. Do not output JSON."
    try:
        ai_result = spitch_ai.process_command(query, system_prompt_override=generative_system_prompt, model='tinyllama')
        ai_response = ai_result.get("response")
        if ai_response:
            speak_func(ai_response)
        else:
            speak_func("I'm sorry, I couldn't generate a creative response for that weather prompt.")
    except Exception as e:
        print(f"AI processing error for weather inquiry: {e}")
        speak_func("I'm having trouble connecting to my AI services to answer that weather question.") 