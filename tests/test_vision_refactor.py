import sys
import os
import json

# Add the project root to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.local_vision_service import _load_mappings, identify_crop_offline, identify_crop

def test_mappings_load():
    print("Testing Mapping Loading...")
    mappings = _load_mappings()
    assert isinstance(mappings, dict), "Mappings should be a dictionary"
    assert "banana" in mappings, "Banana mapping should exist"
    assert "pineapple" not in mappings, "Pineapple (incorrect mapping) should have been removed"
    print("✅ Mappings loaded correctly and are clean.")

def test_mock_inference():
    print("\nTesting Inference Logic (Mocked)...")
    # We verify that IMAGE_NET_MAPPINGS is populated correctly from JSON
    from services.local_vision_service import IMAGE_NET_MAPPINGS
    assert IMAGE_NET_MAPPINGS["lemon"] == "kaji_nemu"
    print(f"✅ 'lemon' correctly maps to '{IMAGE_NET_MAPPINGS['lemon']}'")

def test_unified_strategy():
    print("\nTesting Unified Strategy (Mocked)...")
    # Since we don't have Gemini API key in test environment, 
    # identify_crop should handle the failure and try the offline fallback.
    mock_img = b"fake_image_data"
    mock_crop_data = {"crop_keys": ["rice", "banana"]}
    
    result = identify_crop(mock_img, mock_crop_data)
    assert "crop_key" in result, "Result should have a crop_key"
    print(f"✅ Unified strategy returned: {result['display_name']} ({result['notes']})")
    
if __name__ == "__main__":
    try:
        test_mappings_load()
        test_mock_inference()
        test_unified_strategy()
        print("\nSUMMARY: All vision tests passed!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ AN ERROR OCCURRED: {e}")
