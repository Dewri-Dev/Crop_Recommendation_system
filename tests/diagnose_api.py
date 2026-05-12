import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def diagnose():
    print(f"--- Diagnosing Gemini API ---")
    if not api_key:
        print("❌ ERROR: No API key found in .env file.")
        return

    print(f"✅ API Key found (Length: {len(api_key)})")
    
    # Test a simple text prompt first to check connectivity and key validity
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": "Reply with the word 'SUCCESS' if you can read this."}]}]
    }

    print("📡 Sending test request to Google...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            print("✅ SUCCESS: The API key and internet connection are working!")
            print(f"Response: {response.json()['candidates'][0]['content']['parts'][0]['text'].strip()}")
        else:
            print(f"❌ API ERROR: Status Code {response.status_code}")
            print(f"Details: {response.text}")
    except Exception as e:
        print(f"❌ CONNECTION ERROR: Could not reach Google. {e}")

if __name__ == "__main__":
    diagnose()
