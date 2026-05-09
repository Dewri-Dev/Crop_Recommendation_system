import streamlit as st
import os, base64, json, requests, re, io
from PIL import Image
from utils.logger import logger

def _resize_image(img_bytes, max_px=512, quality=80):
    pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    pil.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()

def _normalise_crop_key(raw, crop_data):
    k = raw.lower().strip().replace(" ", "_").replace("-", "_")
    if k in crop_data["crop_keys"]: return k
    if k in crop_data["aliases"]: return crop_data["aliases"][k]
    for known in crop_data["crop_keys"]:
        if known in k or k in known: return known
    return "rice"

@st.cache_data(ttl=3600, show_spinner=False)
def identify_crop_from_image(img_bytes, crop_data):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            api_key = None
            
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment or streamlit secrets.")
        return {
            "crop_key": "unknown", "display_name": "Unknown", "disease": None,
            "confidence": 0, "notes": "GEMINI_API_KEY is not configured."
        }

    try:
        img_bytes = _resize_image(img_bytes)
    except Exception as e:
        logger.warning(f"Failed to resize image: {e}")
        pass

    b64 = base64.b64encode(img_bytes).decode("utf-8")
    keys_str = ", ".join(crop_data["crop_keys"])
    prompt = (
        "You are an expert agronomist for Assam, India.\n"
        "Look at the image and identify the crop or plant.\n"
        f"Pick ONE key from: [{keys_str}]\n\n"
        "Reply ONLY with JSON, no markdown:\n"
        '{"crop_key":"rice","display_name":"Rice","disease":null,"confidence":90,"notes":"Healthy paddy field"}'
    )
    
    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
                {"text": prompt},
            ]
        }],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 256},
    }
    
    errors = []
    # Attempt multiple flash models for redundancy
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.1-flash", "gemini-3.0-flash", "gemini-2.5-flash"]
    
    for model in models:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model}:generateContent?key={api_key}")
        try:
            resp = requests.post(url, json=payload, timeout=30,
                                 headers={"Content-Type":"application/json"})
            
            if resp.status_code == 404:
                logger.warning(f"Gemini model {model} not found (404).")
                errors.append(f"{model}: model unavailable")
                continue
                
            if resp.status_code != 200:
                try:
                    err_json = resp.json()
                    message = err_json.get("error", {}).get("message", "")
                    reason = err_json.get("error", {}).get("status", "Unknown")
                    full_err = f"{reason}: {message}"
                except Exception:
                    full_err = resp.text[:160]
                
                logger.error(f"Gemini API Error ({model}): {resp.status_code} - {full_err}")
                errors.append(f"{model}: API error {resp.status_code} - {full_err}")
                if resp.status_code in (429, 503):
                    continue
                return {
                    "crop_key": "unknown", "display_name": "Unknown", "disease": None,
                    "confidence": 0, "notes": f"API Error details: {full_err}"
                }

            raw = (resp.json().get("candidates", [{}])[0]
                   .get("content", {}).get("parts", [{}])[0].get("text", "").strip())
            
            clean = re.sub(r"```(?:json)?|```", "", raw).strip()
            m = re.search(r'\{.*\}', clean, re.DOTALL)
            if m: clean = m.group(0)
            
            result = json.loads(clean)
            result["crop_key"] = _normalise_crop_key(result.get("crop_key", "rice"), crop_data)
            logger.info(f"Gemini successfully identified crop: {result['crop_key']} ({result.get('confidence')}%)")
            return result
            
        except Exception as e:
            logger.exception(f"Unexpected error calling Gemini {model}: {e}")
            errors.append(f"{model}: {str(e)}")
            continue
            
    logger.error(f"All Gemini models failed: {'; '.join(errors)}")
    return {
        "crop_key": "unknown", "display_name": "Unknown", "disease": None,
        "confidence": 0, "notes": "; ".join(errors) or "All Gemini models unavailable."
    }
