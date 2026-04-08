# app.py
import streamlit as st
import pickle
import numpy as np
import plotly.graph_objects as go
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

# --- Mode Selection Toggle ---
st.write("### ⚙️ Choose Input Mode")
input_mode = st.radio(
    "Select your technical expertise level:", 
    ["👨‍🌾 Simple Mode (No soil test needed)", "🔬 Advanced Mode (Enter exact lab values)"], 
    horizontal=True
)

st.divider()
st.subheader("📍 Field Information")

# District is required for both modes to fetch live weather
district = st.text_input("Enter District/City (e.g., Guwahati, Jorhat, Tezpur) to fetch live weather:", "Guwahati")

# --- SIMPLE MODE ---
if input_mode == "👨‍🌾 Simple Mode (No soil test needed)":
    col1, col2 = st.columns(2)
    with col1:
        soil_type = st.selectbox("Select General Soil Type", list(soil_properties.keys()))
    with col2:
        season = st.selectbox("Current Season", list(season_rainfall.keys()))
    
    # Auto-calculate values behind the scenes
    N = soil_properties[soil_type]["N"]
    P = soil_properties[soil_type]["P"]
    K = soil_properties[soil_type]["K"]
    ph = soil_properties[soil_type]["ph"]
    rainfall = season_rainfall[season]

# --- ADVANCED MODE ---
else:
    st.info("🔬 Enter exact soil test results below. Live weather will still be fetched automatically for your district.")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        N = st.number_input("Nitrogen (N) Ratio", min_value=0, max_value=150, value=50)
        ph = st.slider("Soil pH Level", min_value=3.0, max_value=9.0, value=6.5, step=0.1)
    with col2:
        P = st.number_input("Phosphorus (P) Ratio", min_value=0, max_value=150, value=50)
        rainfall = st.number_input("Expected Rainfall (mm)", min_value=0.0, max_value=500.0, value=200.0)
    with col3:
        K = st.number_input("Potassium (K) Ratio", min_value=0, max_value=150, value=50)

st.write("") # Add a little blank space

# --- Prediction Button ---
if st.button("Recommend Best Crop 🚀", use_container_width=True):
    with st.spinner("Fetching live weather and analyzing data..."):
        
        # 1. Fetch live weather
        temp, humidity, status = get_live_weather(district)
        
        if temp is None:
            st.error(f"Weather API Error: {status}")
        else:
            # 2. Create the feature array (Must match the exact order of your CSV)
            features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
            
            # 3. Make Prediction with Probabilities (Smart AI)
            probabilities = rf_model.predict_proba(features)[0]
            
            # Get the indices of the top 3 highest probabilities
            top_3_indices = np.argsort(probabilities)[::-1][:3]
            top_3_probs = probabilities[top_3_indices]
            
            # Decode the numbers back into crop names
            top_3_crops = label_encoder.inverse_transform(top_3_indices)
            
            # --- Display Results ---
            # --- UPGRADE 4: EXPLAINABLE AI (XAI) & VISUALS ---
            st.success("Analysis Complete!")
            
            # --- The #1 Spotlight ---
            best_crop = top_3_crops[0]
            best_crop_formatted = best_crop.replace("_", " ").title()
            best_confidence = top_3_probs[0] * 100
            
            st.markdown(f"## 🏆 Top Recommendation: **<span style='color:green'>{best_crop_formatted}</span>**", unsafe_allow_html=True)
            
           # Show Image and Explanation Side-by-Side
            from mappings import crop_images 
            
            # --- SMART IMAGE LOGIC FOR ALL 49 CROPS ---
            if best_crop in crop_images:
                # 1. If you manually added a photo in mappings.py, use it!
                img_url = crop_images[best_crop]
            else:
                # 2. If no photo exists yet, automatically generate a custom one with the crop's name
                url_name = best_crop_formatted.replace(" ", "+")
                img_url = f"https://placehold.co/800x600/2E8B57/white?text={url_name}"
            
            img_col, text_col = st.columns([1, 2])
            
            with img_col:
                st.image(img_url, use_container_width=True, caption=best_crop_formatted)
                
            with text_col:
                st.write(f"**AI Confidence Score:** {best_confidence:.1f}%")
                
                # Dynamic Logic Generator (Explainable AI)
                st.info(f"**Why did the AI choose {best_crop_formatted}?** \n\n"
                        f"This crop thrives in environments with a temperature around **{temp}°C** and **{humidity}% humidity**. "
                        f"Additionally, your soil's **pH of {ph}** and the expected **{rainfall} mm of rainfall** perfectly match "
                        f"the historical growing conditions for this specific crop in Assam.")
            
            st.divider() # Adds a clean horizontal line
            
            # --- The Runners Up ---
            st.markdown("### 🌱 **Alternative Options**")
            
            # Loop through the remaining top crops (skipping the 1st one)
            for i in range(1, 3):
                crop_name = top_3_crops[i].replace("_", " ").title()
                confidence_pct = top_3_probs[i] * 100
                
                col_name, col_pct = st.columns([3, 1])
                with col_name:
                    st.write(f"**{i+1}. {crop_name}**")
                with col_pct:
                    st.write(f"**{confidence_pct:.1f}% Match**")
                st.progress(float(top_3_probs[i]))
            
            st.divider()
            
            # --- UPGRADE 3: INTERACTIVE DATA DASHBOARD ---
            st.markdown("### 📊 Environmental Analysis")
            st.write("Visualizing the data used to make this recommendation:")
            
            # Create a 3-column layout for the gauges and radar chart
            dash_col1, dash_col2, dash_col3 = st.columns(3)
            
            # 1. Temperature Gauge
            with dash_col1:
                fig_temp = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = temp,
                    title = {'text': "Temperature (°C)", 'font': {'size': 16}},
                    gauge = {
                        'axis': {'range': [0, 50], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "red"},
                        'steps': [
                            {'range': [0, 20], 'color': "lightblue"},
                            {'range': [20, 35], 'color': "lightgreen"},
                            {'range': [35, 50], 'color': "salmon"}
                        ]
                    }
                ))
                fig_temp.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_temp, use_container_width=True)
                
            # 2. Humidity Gauge
            with dash_col2:
                fig_hum = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = humidity,
                    title = {'text': "Humidity (%)", 'font': {'size': 16}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "blue"},
                        'steps': [
                            {'range': [0, 40], 'color': "lightgray"},
                            {'range': [40, 70], 'color': "lightgreen"},
                            {'range': [70, 100], 'color': "lightblue"}
                        ]
                    }
                ))
                fig_hum.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_hum, use_container_width=True)

            # 3. NPK Radar Chart
            with dash_col3:
                fig_npk = go.Figure(data=go.Scatterpolar(
                    r=[N, P, K, N], 
                    theta=['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Nitrogen (N)'],
                    fill='toself',
                    line_color='forestgreen'
                ))
                fig_npk.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, 
                            range=[0, max(150, max(N, P, K) + 10)],
                            tickfont=dict(color="black", size=12)  # <--- THIS IS THE FIX
                        )
                    ),
                    showlegend=False,
                    title={'text': "Soil NPK Balance", 'font': {'size': 16}, 'x': 0.5},
                    height=250, margin=dict(l=25, r=25, t=40, b=25)
                )
                st.plotly_chart(fig_npk, use_container_width=True)
            
            # Small text summary at the bottom
            st.caption(f"Estimated Soil pH: **{ph}** | Expected Rainfall: **{rainfall} mm**")