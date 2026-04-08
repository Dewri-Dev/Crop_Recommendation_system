# app.py
import streamlit as st
import pickle
import numpy as np
from mappings import soil_properties, season_rainfall
from weather import get_live_weather

# --- Page Configuration ---
st.set_page_config(page_title="Assam Crop Recommender", page_icon="🌾", layout="centered")

# --- Load ML Models ---
@st.cache_resource # Caches the model so it doesn't reload on every click
def load_models():
    model = pickle.load(open("model/crop_model.pkl", "rb"))
    encoder = pickle.load(open("model/label_encoder.pkl", "rb"))
    return model, encoder

try:
    rf_model, label_encoder = load_models()
except FileNotFoundError:
    st.error("Model files not found! Please run train_model.ipynb first.")
    st.stop()

# --- User Interface ---
st.title("🌾 AI Crop Recommendation System")
st.markdown("**Tailored for the farmers of Assam using real-time weather data.**")

# Input Section
st.subheader("📍 Field Information")
col1, col2 = st.columns(2)

with col1:
    district = st.text_input("Enter District/City (e.g., Guwahati, Jorhat, Tezpur)", "Guwahati")
    soil_type = st.selectbox("Select General Soil Type", list(soil_properties.keys()))

with col2:
    season = st.selectbox("Current Season", list(season_rainfall.keys()))

# Prediction Button
if st.button("Recommend Best Crop 🚀", use_container_width=True):
    with st.spinner("Fetching live weather and analyzing data..."):
        
        # 1. Fetch live weather
        temp, humidity, status = get_live_weather(district)
        
        if temp is None:
            st.error(f"Weather API Error: {status}")
        else:
            # 2. Map simple inputs to numerical features
            N = soil_properties[soil_type]["N"]
            P = soil_properties[soil_type]["P"]
            K = soil_properties[soil_type]["K"]
            ph = soil_properties[soil_type]["ph"]
            rainfall = season_rainfall[season]
            
            # 3. Create the feature array (Must match the exact order of your CSV: N, P, K, temp, hum, ph, rain)
            features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
            
            # 4. Make Prediction
            prediction_num = rf_model.predict(features)[0]
            recommended_crop = label_encoder.inverse_transform([prediction_num])[0]
            
            # --- Display Results ---
            st.success("Analysis Complete!")
            
            # Format crop name beautifully (e.g., "assam_tea" -> "Assam Tea")
            formatted_crop = recommended_crop.replace("_", " ").title()
            
            st.markdown(f"""
            ### 🌱 **Highly Recommended Crop:** ## **<span style='color:green'>{formatted_crop}</span>**
            """, unsafe_allow_html=True)
            
            # Show the data used behind the scenes
            with st.expander("📊 View the Environmental Data Used"):
                st.write(f"**Live Temperature:** {temp} °C")
                st.write(f"**Live Humidity:** {humidity} %")
                st.write(f"**Estimated Rainfall:** {rainfall} mm")
                st.write(f"**Estimated Soil pH:** {ph}")