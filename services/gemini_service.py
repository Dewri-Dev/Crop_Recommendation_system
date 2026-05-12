import requests
import json
import os
import base64
from utils.logger import logger
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

class RateLimitException(Exception):
    """Custom exception to trigger tenacity retries on 429 errors."""
    pass

class GeminiVisionService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Using the stable flash-latest identifier we verified earlier
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={self.api_key}"
        self.headers = {'Content-Type': 'application/json'}

    @retry(
        retry=retry_if_exception_type(RateLimitException),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=lambda retry_state: logger.warning(f"Rate limit hit. Retrying in {retry_state.next_action.sleep}s... (Attempt {retry_state.attempt_number})")
    )
    def _call_gemini_api(self, payload):
        """Internal helper to call the API with retry logic."""
        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Raise custom exception to trigger @retry decorator
            raise RateLimitException("Gemini API Quota Exceeded")
        else:
            logger.error(f"Gemini API Error: {response.status_code} - {response.text}")
            return None

    def identify_crop(self, img_bytes, crop_list):
        """
        Uses Gemini AI to identify a crop from bytes.
        Includes Exponential Backoff to handle rate limits gracefully.
        """
        if not self.api_key:
            logger.error("Gemini API Key missing.")
            return None

        # Prepare base64 image
        image_data = base64.b64encode(img_bytes).decode('utf-8')

        prompt = f"""
        Analyze this image of a crop or plant. 
        Identify which of the following supported crops it is: {', '.join(crop_list)}.
        
        Return ONLY a JSON object with this exact format:
        {{
            "crop_key": "the_matching_key_or_unknown",
            "confidence": 0.0 to 1.0,
            "reasoning": "briefly explain why you identified it as this crop"
        }}
        """

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        }

        try:
            result = self._call_gemini_api(payload)
            if result:
                content = result['candidates'][0]['content']['parts'][0]['text']
                # Clean up JSON if LLM added markdown wrappers
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Gemini Service Exhausted Retries or Failed: {e}")
            return None

gemini_service = GeminiVisionService()
