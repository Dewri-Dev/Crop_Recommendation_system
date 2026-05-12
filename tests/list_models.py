import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def list_models():
    print(f"--- Listing Available Gemini Models ---")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Found {len(models)} models:")
            for m in models:
                print(f" - {m['name']} (Supports: {', '.join(m['supportedGenerationMethods'])})")
        else:
            print(f"❌ API ERROR: Status Code {response.status_code}")
            print(f"Details: {response.text}")
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    list_models()
