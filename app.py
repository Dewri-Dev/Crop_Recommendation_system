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

try:
    with open("config/crop_info.json", "r", encoding="utf-8") as f:
        CROP_DATA = json.load(f)
except:
    CROP_DATA = {}

# --- 2. AI & PLOTS ---
def get_ai_advice(crop, n, p, k, temp):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"1 short farming tip for {crop} in Assam (Soil N:{n}, P:{p}, K:{k}, Temp:{temp}C)."
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=80)
        return res.choices[0].message.content
    except: return "No AI tip available. Follow standard practices."

def get_analytics_plots():
    sns.set_theme(style="whitegrid")
    
    # 1. Crop Distribution
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    df['label'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax1, colors=sns.color_palette("Set3"))
    ax1.set_title("Crop Distribution")
    ax1.set_ylabel("")

    # 2. Soil pH
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    sns.histplot(df['ph'], bins=15, color='#4CAF50', ax=ax2)
    ax2.set_title("Soil pH Distribution")

    # 3. Rainfall
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    sns.histplot(df['rainfall'], bins=15, color='#1976D2', ax=ax3)
    ax3.set_title("Rainfall Distribution")

    # 4. Temp vs Humidity
    fig4, ax4 = plt.subplots(figsize=(5, 4))
    sns.scatterplot(data=df, x='temperature', y='humidity', color='#2E7D32', alpha=0.5, ax=ax4)
    ax4.set_title("Temperature vs Humidity")
    
    return fig1, fig2, fig3, fig4

# --- 3. CORE LOGIC ---
def advisor(n, p, k, ph, rain, district, soil, flood):
    temp, hum, _ = get_live_weather(district)
    if not temp: return "Error fetching weather data."

    features = np.array([[n, p, k, temp, hum, ph, rain]])
    
    # Get Top 5 Predictions
    try:
        probs = model.predict_proba(features)[0]
        top_5_idx = np.argsort(probs)[-5:][::-1]
        top_5_crops = le.inverse_transform(top_5_idx)
        top_5_probs = probs[top_5_idx]
    except:
        prediction = model.predict(features)
        top_5_crops = [le.inverse_transform(prediction)[0]]
        top_5_probs = [1.0]

    primary_crop = top_5_crops[0].lower()
    crop_info = CROP_DATA.get(primary_crop, {})
    local_name = crop_info.get("local_name", primary_crop.upper())
    recovery_tip = crop_info.get("recovery", "Follow standard practices.")
    
    advice = get_ai_advice(primary_crop, n, p, k, temp)
    flood_msg = f"\n\n🚨 **FLOOD RECOVERY:** {recovery_tip}" if flood else ""

    top_list = "### 🔝 Top 5 Recommendations:\n"
    for i, (c, prob) in enumerate(zip(top_5_crops, top_5_probs)):
        l_name = CROP_DATA.get(c.lower(), {}).get("local_name", c.upper())
        top_list += f"{i+1}. **{l_name}** ({prob*100:.1f}%)\n"

    return f"""
    {top_list}
    
    ---
    🌟 **PRIMARY CHOICE: {local_name}**
    
    Location Snapshot ({district}):
    - 🌡️ Temp: {temp}°C | 💧 Humidity: {hum}% | 🧪 Soil: {soil}
    
    💡 AI Expert Tip:
    "{advice}"
    {flood_msg}
    """

# --- 4. UI CONSTRUCTION ---
with gr.Blocks(title="Assam Crop Advisor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚜 Assam Crop Advisor & Analytics")
    
    with gr.Tabs():
        with gr.TabItem("🌱 Crop Advisor"):
            with gr.Row():
                with gr.Column():
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
                
                with gr.Column():
                    output = gr.Markdown("### Results will appear here...")

        with gr.TabItem("📊 Analytics"):
            p1, p2, p3, p4 = get_analytics_plots()
            with gr.Row():
                gr.Plot(p1, label="Crop Distribution")
                gr.Plot(p2, label="Soil pH")
            with gr.Row():
                gr.Plot(p3, label="Rainfall")
                gr.Plot(p4, label="Temp vs Humidity")

    # Link logic
    btn.click(
        fn=advisor, 
        inputs=[n, p, k, ph, rain, district, soil, flood], 
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()
