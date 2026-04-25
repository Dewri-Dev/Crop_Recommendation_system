# weather.py
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_live_weather(city_name):
    """Fetches live temperature and humidity for a given city."""
    api_key = os.getenv("WEATHER_API_KEY", "d5455bca1b684b756d6aaad8233f25da")
    
    if not api_key:
        return None, None, "API Key is missing! Check your .env file."

    # OpenWeatherMap API endpoint
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            return temp, humidity, "Success"
        else:
            return None, None, f"Error fetching weather: {data.get('message', 'Unknown error')}"
            
    except Exception as e:
        return None, None, f"Connection error: {e}"