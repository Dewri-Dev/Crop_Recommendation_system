import gradio as gr
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from dotenv import load_dotenv
from weather import get_live_weather
from groq import Groq

load_dotenv()

# --- 1. DATA & MODELS ---
model = pickle.load(open("model/crop_model.pkl", "rb"))
le = pickle.load(open("model/label_encoder.pkl", "rb"))
df = pd.read_csv("data/Crop_recommendation.csv")

# Load Localized Assam Crop Data from JSON
try:
    with open("config/crop_info.json", "r", encoding="utf-8") as f:
        CROP_DATA = json.load(f)
except Exception as e:
    print(f"Error loading crop_info.json: {e}")
    CROP_DATA = {}

# --- 2. AI & PLOTS ---
def get_ai_advice(crop, n, p, k, temp):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"1 short farming tip for {crop} in Assam (Soil N:{n}, P:{p}, K:{k}, Temp:{temp}C)."
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=80)
        return res.choices[0].message.content
    except: return "No AI tip available. Follow standard practices."

def get_graph():
    fig, ax = plt.subplots(figsize=(10, 3))
    sns.barplot(x=['N', 'P', 'K'], y=[df['N'].mean(), df['P'].mean(), df['K'].mean()], palette="viridis", ax=ax)
    plt.title("Regional Nutrient Averages")
    return fig

# --- 3. CORE LOGIC ---
def advisor(n, p, k, ph, rain, district, soil, flood):
    # Fetch Weather
    temp, hum, _ = get_live_weather(district)
    if not temp: return "Error fetching weather data."

    # ML Prediction (Must provide 7 features in exact order)
    features = np.array([[n, p, k, temp, hum, ph, rain]])
    prediction = model.predict(features)
    crop = le.inverse_transform(prediction)[0].lower()
    
    # Metadata Lookup
    crop_info = CROP_DATA.get(crop, {})
    local_name = crop_info.get("local_name", crop.upper())
    recovery_tip = crop_info.get("recovery", "Follow standard practices.")
    
    # Generate Output
    advice = get_ai_advice(crop, n, p, k, temp)
    flood_msg = f"\n\n🚨 **FLOOD RECOVERY:** {recovery_tip}" if flood else ""

    return f"""
    🌿 RECOMMENDED: {local_name}
    
    Location Snapshot ({district}):
    - 🌡️ Temp: {temp}°C | 💧 Humidity: {hum}% | 🧪 Soil: {soil}
    
    💡 AI Expert Tip:
    "{advice}"
    {flood_msg}
    """

# --- 4. SIMPLE UI ---
with gr.Blocks(title="Assam Crop Advisor") as demo:
    gr.Markdown(" 🚜 Assam Crop Advisor")
    
    with gr.Row():
        n = gr.Number(label="Nitrogen (N)", value=80)
        p = gr.Number(label="Phosphorus (P)", value=40)
        k = gr.Number(label="Potassium (K)", value=40)
    
    with gr.Row():
        ph = gr.Slider(0, 14, label="Soil pH", value=6.5)
        rain = gr.Number(label="Expected Rainfall (mm)", value=200)
    
    with gr.Row():
        district = gr.Dropdown(["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur", "Nagaon"], label="District", value="Guwahati")
        soil = gr.Dropdown(["Alluvial", "Clayey", "Sandy Loam"], label="Soil Type", value="Alluvial")
        flood = gr.Checkbox(label="Flood Affected Area?")
    
    btn = gr.Button("Get Advisor Results", variant="primary")
    output = gr.Markdown()
    
    with gr.Accordion("📊 Dataset Nutrient Averages", open=False):
        gr.Plot(get_graph())

    # Link logic
    btn.click(
        fn=advisor, 
        inputs=[n, p, k, ph, rain, district, soil, flood], 
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(share=True)
