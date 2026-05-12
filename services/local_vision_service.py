from utils.logger import logger
from services.gemini_service import gemini_service

def identify_crop_ai(img_bytes, crop_data):
    """
    Identifies a crop using Google Gemini AI.
    Provides high accuracy and doesn't require local model weights.
    """
    logger.info("Identifying crop using Gemini AI...")
    
    supported_crops = crop_data.get("crop_keys", [])
    gemini_result = gemini_service.identify_crop(img_bytes, supported_crops)
    
    if gemini_result and gemini_result.get("crop_key") != "unknown":
        return {
            "crop_key": gemini_result["crop_key"],
            "display_name": gemini_result["crop_key"].replace("_", " ").title(),
            "confidence": round(gemini_result["confidence"] * 100, 1),
            "notes": f"Gemini Cloud AI: {gemini_result.get('reasoning')}"
        }
    
    # Handle unknown or failed cases
    display_name = "Unknown"
    if gemini_result and gemini_result.get("crop_key") == "unknown":
        notes = f"Gemini AI could not confidently match this to our supported crops. Reason: {gemini_result.get('reasoning')}"
    else:
        notes = "Gemini AI failed to process the image. Please check your internet connection or API key."

    return {
        "crop_key": "unknown",
        "display_name": display_name,
        "confidence": 0,
        "notes": notes
    }
