import requests
import os
from dotenv import load_dotenv

# Load the API Key from the .env file
load_dotenv()

def get_live_weather(city_name):
    """
    This function connects to OpenWeatherMap API.
    It takes a city name (like 'Guwahati') and returns (Temperature, Humidity, Status).
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    # The URL contains: the city name, your API key, and 'units=metric' for Celsius
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    
    try:
        # 1. Send the request to the internet
        response = requests.get(url, timeout=10)
        
        # 2. Convert the raw response into a Python Dictionary (JSON)
        data = response.json()
        
        if response.status_code == 200:
            # 3. Extract the specific numbers we need for our AI model
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            return temp, humidity, "Success"
        else:
            return None, None, f"Error: {data.get('message')}"
            
    except Exception as e:
        return None, None, f"Connection Failed: {e}"
