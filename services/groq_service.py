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

class ServiceUnavailableException(Exception):
    """Custom exception to trigger tenacity retries on 5xx errors."""
    pass

class GroqVisionService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    @retry(
        retry=(retry_if_exception_type(RateLimitException) | retry_if_exception_type(ServiceUnavailableException)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=lambda retry_state: logger.warning(f"Groq API issue (Attempt {retry_state.attempt_number}). Retrying in {retry_state.next_action.sleep}s...")
    )
    def _call_groq_api(self, payload):
        """Internal helper to call the Groq API with retry logic."""
        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise RateLimitException("Groq API Quota Exceeded")
        elif response.status_code in [500, 503, 504]:
            raise ServiceUnavailableException(f"Groq API Server Error: {response.status_code}")
        else:
            logger.error(f"Groq API Error: {response.status_code} - {response.text}")
            return None

    def identify_crop(self, img_bytes, crop_list):
        """
        Uses Groq Llama 4 Vision to identify a crop from bytes.
        """
        if not self.api_key:
            logger.error("Groq API Key missing.")
            return None

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
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            result = self._call_groq_api(payload)
            if result:
                content = result['choices'][0]['message']['content']
                return json.loads(content)
        except Exception as e:
            logger.error(f"Groq Service Exhausted Retries or Failed: {e}")
            return None

groq_service = GroqVisionService()
