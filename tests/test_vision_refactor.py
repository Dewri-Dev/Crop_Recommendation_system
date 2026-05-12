import sys
import os
import json

# Add the project root to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.local_vision_service import _load_mappings, identify_crop_offline

def test_mappings_load():
    print("Testing Mapping Loading...")
    mappings = _load_mappings()
    assert isinstance(mappings, dict), "Mappings should be a dictionary"
    assert "banana" in mappings, "Banana mapping should exist"
    assert "pineapple" not in mappings, "Pineapple (incorrect mapping) should have been removed"
    print("✅ Mappings loaded correctly and are clean.")

def test_mock_inference():
    print("\nTesting Inference Logic (Mocked)...")
    # We won't actually run the model (it's slow/needs GPU), 
    # but we can test if the logic handles the mappings correctly.
    # Note: In a real project, we'd use 'unittest.mock' here.
    
    # For this simple check, we'll verify that IMAGE_NET_MAPPINGS is populated
    from services.local_vision_service import IMAGE_NET_MAPPINGS
    assert IMAGE_NET_MAPPINGS["lemon"] == "kaji_nemu"
    print(f"✅ 'lemon' correctly maps to '{IMAGE_NET_MAPPINGS['lemon']}'")
    
if __name__ == "__main__":
    try:
        test_mappings_load()
        test_mock_inference()
        print("\nSUMMARY: All vision mapping tests passed!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ AN ERROR OCCURRED: {e}")
