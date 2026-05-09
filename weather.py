# weather.py
import requests
import os
from dotenv import load_dotenv
from utils.logger import logger

# Load environment variables from .env file
load_dotenv()

def get_live_weather(city_name):
    """Fetches live temperature and humidity for a given city."""
    api_key = os.getenv("WEATHER_API_KEY")
    
    # Fallback only if absolutely necessary, but log it as a warning
    if not api_key:
        api_key = "d5455bca1b684b756d6aaad8233f25da"
        logger.warning("WEATHER_API_KEY not found in .env, using fallback key.")

    # OpenWeatherMap API endpoint
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            logger.info(f"Weather fetched for {city_name}: {temp}°C, {humidity}% humidity")
            return temp, humidity, "Success"
        else:
            error_msg = data.get('message', 'Unknown error')
            logger.error(f"Weather API Error ({response.status_code}) for {city_name}: {error_msg}")
            return None, None, f"Error fetching weather: {error_msg}"
            
    except Exception as e:
        logger.exception(f"Connection error while fetching weather for {city_name}: {e}")
        return None, None, f"Connection error: {e}"
