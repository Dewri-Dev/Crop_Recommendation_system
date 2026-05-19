import pickle
import numpy as np
import pandas as pd
from weather import get_live_weather

def test_full_prediction():
    try:
        print("1. Loading assets...")
        model = pickle.load(open("model/crop_model.pkl", "rb"))
        le = pickle.load(open("model/label_encoder.pkl", "rb"))
        
        # Simulated inputs
        n, p, k = 80, 40, 40
        ph = 6.5
        rainfall = 200
        district = "Guwahati"
        
        print(f"2. Fetching weather for {district}...")
        temp, hum, status = get_live_weather(district)
        
        if temp:
            print(f"   Success: {temp}C, {hum}%")
            print("3. Running ML Inference...")
            features = np.array([[n, p, k, temp, hum, ph, rainfall]])
            prediction = model.predict(features)
            crop = le.inverse_transform(prediction)[0]
            print(f"4. Result: {crop.upper()}")
            return True
        else:
            print(f"   Weather API Failed: {status}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

if __name__ == "__main__":
    test_full_prediction()
