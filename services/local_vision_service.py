import os
import json
import io
import urllib.request
from PIL import Image
from utils.logger import logger
from services.groq_service import groq_service

# Path to the mapping configuration
MAPPINGS_PATH = "config/vision_mappings.json"
MODEL_NAME = 'mobilenetv3_large_100.ra_in1k'
LABELS_URL = "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt"
LABELS_PATH = "model/imagenet_labels.txt"

def _load_mappings():
    """Loads ImageNet to system crop mappings from JSON."""
    try:
        if os.path.exists(MAPPINGS_PATH):
            with open(MAPPINGS_PATH, 'r') as f:
                data = json.load(f)
                return data.get("IMAGE_NET_MAPPINGS", {})
        else:
            logger.error(f"Mapping file not found at {MAPPINGS_PATH}")
            return {}
    except Exception as e:
        logger.error(f"Error loading mappings: {e}")
        return {}

# Global mappings for quick access and test compatibility
IMAGE_NET_MAPPINGS = _load_mappings()

def _ensure_labels():
    """Downloads ImageNet labels if missing."""
    if not os.path.exists(LABELS_PATH):
        if not os.path.exists("model"): os.makedirs("model")
        try:
            logger.info("Downloading ImageNet labels...")
            urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)
        except Exception as e:
            logger.error(f"Failed to download labels: {e}")

def _get_inference_tools():
    """Lazily loads torch and timm models."""
    try:
        import torch
        import timm
        import streamlit as st
        
        @st.cache_resource(show_spinner=False)
        def _load_model():
            _ensure_labels()
            logger.info(f"Loading pre-trained vision model: {MODEL_NAME}")
            try:
                model = timm.create_model(MODEL_NAME, pretrained=True)
                model.eval()
                data_config = timm.data.resolve_model_data_config(model)
                transforms = timm.data.create_transform(**data_config, is_training=False)
                with open(LABELS_PATH, 'r') as f:
                    labels = [line.strip() for line in f.readlines()]
                return model, transforms, labels
            except Exception as e:
                logger.exception(f"Failed to load vision model: {e}")
                return None, None, None
        
        return _load_model()
    except ImportError:
        return None, None, None

def identify_crop_ai(img_bytes, crop_data):
    """
    Identifies a crop using Groq Cloud AI (Llama 4).
    Provides high accuracy and doesn't require local model weights.
    """
    logger.info("Identifying crop using Groq Cloud AI...")
    
    supported_crops = crop_data.get("crop_keys", [])
    groq_result = groq_service.identify_crop(img_bytes, supported_crops)
    
    if groq_result and groq_result.get("crop_key") != "unknown":
        return {
            "crop_key": groq_result["crop_key"],
            "display_name": groq_result["crop_key"].replace("_", " ").title(),
            "confidence": round(groq_result["confidence"] * 100, 1),
            "notes": f"Groq Cloud AI: {groq_result.get('reasoning')}"
        }
    
    # Handle unknown or failed cases
    display_name = "Unknown"
    if groq_result and groq_result.get("crop_key") == "unknown":
        notes = f"Groq AI could not confidently match this to our supported crops. Reason: {groq_result.get('reasoning')}"
    else:
        notes = "Groq AI failed to process the image. Please check your internet connection or API key."

    return {
        "crop_key": "unknown",
        "display_name": display_name,
        "confidence": 0,
        "notes": notes
    }

def identify_crop_offline(img_bytes, crop_data=None):
    """
    Identifies a crop using a local pre-trained model (MobileNetV3).
    Fallback for when internet is unavailable or Groq fails.
    """
    model, transforms, labels = _get_inference_tools()
    
    if model is None:
        return {
            "crop_key": "unknown",
            "display_name": "Offline Mode Unavailable",
            "confidence": 0,
            "notes": "Offline vision dependencies (torch, timm) not found or model failed to load."
        }

    try:
        import torch
        # 1. Preprocess
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        input_tensor = transforms(img).unsqueeze(0)

        # 2. Predict
        with torch.no_grad():
            output = model(input_tensor)

        # 3. Process probabilities
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top_prob, top_idx = torch.topk(probabilities, 5)

        best_crop_key = "unknown"
        best_display_name = "Unknown Plant"
        best_conf = 0.0

        # 4. Smart Mapping (Using Global IMAGE_NET_MAPPINGS)
        for i in range(5):
            prob = top_prob[i].item() * 100
            idx = top_idx[i].item()
            label_text = labels[idx].lower()

            for keyword, system_key in IMAGE_NET_MAPPINGS.items():
                if keyword in label_text:
                    best_crop_key = system_key
                    best_display_name = label_text.title()
                    best_conf = prob
                    break
            if best_crop_key != "unknown": break

        # 5. Final Result
        if best_crop_key == "unknown":
            top_label = labels[top_idx[0].item()].title()
            return {
                "crop_key": "unknown",
                "display_name": "Unknown",
                "confidence": 0,
                "notes": f"AI detected '{top_label}', which is not a supported crop."
            }

        return {
            "crop_key": best_crop_key,
            "display_name": best_display_name,
            "confidence": round(best_conf, 1),
            "notes": "Verified by local MobileNetV3 (Offline Fallback)."
        }

    except Exception as e:
        logger.exception(f"Offline vision inference error: {e}")
        return {
            "crop_key": "unknown",
            "display_name": "Inference Error",
            "confidence": 0,
            "notes": f"Error: {str(e)}"
        }

def identify_crop(img_bytes, crop_data):
    """
    Unified entry point for crop identification.
    Strategy: Try Groq AI first, fall back to Offline MobileNetV3 if needed.
    """
    # 1. Try Groq AI (Cloud)
    result = identify_crop_ai(img_bytes, crop_data)
    
    # 2. If Groq fails or is 'unknown', try Offline Fallback
    if result.get("crop_key") == "unknown":
        logger.info("Groq AI returned 'unknown' or failed. Attempting offline fallback...")
        offline_result = identify_crop_offline(img_bytes, crop_data)
        
        # Only use offline result if it actually found something
        if offline_result.get("crop_key") != "unknown":
            return offline_result
            
    return result
