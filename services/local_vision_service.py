import torch
import timm
from PIL import Image
import io
import os
import streamlit as st
from utils.logger import logger
import urllib.request

# ─── Configuration ───
# We use a high-performance, lightweight model: MobileNet-V3 Large
MODEL_NAME = 'mobilenetv3_large_100.ra_in1k'
LABELS_URL = "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt"
LABELS_PATH = "model/imagenet_labels.txt"

# Mapping ImageNet labels (which are general) to our system's specific crop keys
# This dictionary translates the AI's "Science Brain" to our "Farmer Brain"
IMAGE_NET_MAPPINGS = {
    "corn": "maize",
    "ear, spike, berry": "maize",
    "rice, paddy": "rice",
    "banana": "banana",
    "lemon": "kaji_nemu",
    "orange": "orange",
    "granny smith": "apple",
    "bell pepper": "bhut_jolokia",
    "chili, chili pepper": "bhut_jolokia",
    "pineapple": "ou_tenga",
    "pomegranate": "pomegranate",
    "fig": "leteku",
    "custard apple": "thekera",
    "coconut": "coconut",
    "coffee, coffeepot": "coffee",
    "pot, flowerpot": "assam_tea", # Tea gardens often look like general foliage/pots to basic AI
    "wheat": "wheat"
}

def _ensure_labels():
    """Downloads ImageNet labels if missing."""
    if not os.path.exists(LABELS_PATH):
        if not os.path.exists("model"): os.makedirs("model")
        try:
            logger.info("Downloading ImageNet labels...")
            urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)
        except Exception as e:
            logger.error(f"Failed to download labels: {e}")

@st.cache_resource(show_spinner=False)
def _load_pretrained_model():
    """Loads the pre-trained model and its specific transforms."""
    _ensure_labels()
    logger.info(f"Loading pre-trained vision model: {MODEL_NAME}")
    try:
        model = timm.create_model(MODEL_NAME, pretrained=True)
        model.eval()
        
        # Load data configuration (resizing, mean/std normalization)
        data_config = timm.data.resolve_model_data_config(model)
        transforms = timm.data.create_transform(**data_config, is_training=False)
        
        # Load labels into a list
        with open(LABELS_PATH, 'r') as f:
            labels = [line.strip() for line in f.readlines()]
            
        return model, transforms, labels
    except Exception as e:
        logger.exception(f"Failed to load pre-trained vision model: {e}")
        return None, None, None

def identify_crop_offline(img_bytes, crop_data):
    """
    Identifies a crop using a pre-trained specialist model.
    Zero training required. Works fully offline after first download.
    """
    model, transforms, labels = _load_pretrained_model()
    
    if model is None:
        return {
            "crop_key": "unknown", "display_name": "Error", "disease": None,
            "confidence": 0, "notes": "Vision engine failed to load. Check logs."
        }

    try:
        # 1. Preprocess
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        input_tensor = transforms(img).unsqueeze(0)

        # 2. Predict
        with torch.no_grad():
            output = model(input_tensor)
            
        # 3. Process probabilities
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top_prob, top_idx = torch.topk(probabilities, 5) # Check top 5 matches
        
        best_crop_key = "unknown"
        best_display_name = "Unknown Plant"
        best_conf = 0.0
        
        # 4. Smart Mapping
        # We look through the top 5 predictions to see if any match our crop mappings
        for i in range(5):
            prob = top_prob[i].item() * 100
            idx = top_idx[i].item()
            label_text = labels[idx].lower()
            
            logger.debug(f"Offline AI match {i+1}: {label_text} ({prob:.1f}%)")
            
            for keyword, system_key in IMAGE_NET_MAPPINGS.items():
                if keyword in label_text:
                    best_crop_key = system_key
                    best_display_name = label_text.title()
                    best_conf = prob
                    break
            
            if best_crop_key != "unknown":
                break
        
        # 5. Final fallback (use top result even if no mapping found)
        if best_crop_key == "unknown":
            best_display_name = labels[top_idx[0].item()].title()
            best_conf = top_prob[0].item() * 100
            logger.warning(f"AI saw '{best_display_name}' but no system mapping found.")
            return {
                "crop_key": "unknown",
                "display_name": "Unknown",
                "disease": None,
                "confidence": 0,
                "notes": f"AI detected '{best_display_name}', which is not a supported crop in our system. Please upload a valid crop image."
            }

        return {
            "crop_key": best_crop_key,
            "display_name": best_display_name,
            "disease": None,
            "confidence": round(best_conf, 1),
            "notes": "Verified by local MobileNetV3 (No Cloud Required)."
        }

    except Exception as e:
        logger.exception(f"Offline vision inference error: {e}")
        return {"crop_key": "unknown", "display_name": "Inference Error", "disease": None,
                "confidence": 0, "notes": f"Error: {str(e)}"}
