import os
import json
from services.local_vision_service import identify_crop_ai
from utils.logger import logger

# Mocking CROP_DATA for the test
with open("config/crop_data.json", "r", encoding="utf-8") as f:
    CROP_DATA = json.load(f)

IMAGE_DIR = "images"
EXPECTED_MAPPINGS = {
    "amlokhi.jpg": "amlokhi",
    "bao_rice.jpg": "rice",
    "coconut.jpg": "coconut",
    "dhekia_xaak.jpg": "dhekia_xaak",
}

def run_vision_audit():
    print("🚀 STARTING VISION ACCURACY AUDIT\n" + "="*40)
    supported_crops = CROP_DATA.get("crop_keys", [])
    
    results = []
    for img_name, expected_key in EXPECTED_MAPPINGS.items():
        img_path = os.path.join(IMAGE_DIR, img_name)
        if not os.path.exists(img_path):
            print(f"⚠️ Missing: {img_name}")
            continue
            
        print(f"Testing {img_name}...")
        try:
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            
            # Call our live AI service
            result = identify_crop_ai(img_bytes, CROP_DATA)
            
            detected_key = result["crop_key"]
            confidence = result["confidence"]
            
            status = "✅ PASS" if detected_key == expected_key else "❌ FAIL"
            results.append({
                "image": img_name,
                "expected": expected_key,
                "detected": detected_key,
                "confidence": confidence,
                "status": status,
                "notes": result.get("notes", "")
            })
            print(f"  Result: {status} ({detected_key} at {confidence}%)")
            
        except Exception as e:
            print(f"  🔥 ERROR processing {img_name}: {e}")

    print("\n" + "="*40 + "\n📊 AUDIT SUMMARY")
    for r in results:
        print(f"{r['status']} | {r['image']} -> {r['detected']} ({r['confidence']}%)")
        if r['status'] == "❌ FAIL":
             print(f"    Expected: {r['expected']}")

if __name__ == "__main__":
    run_vision_audit()
