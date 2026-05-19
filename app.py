import gradio as gr
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import requests
from dotenv import load_dotenv
from weather import get_live_weather
from groq import Groq

# Load environment variables
load_dotenv()

# 1. LOAD ASSETS
def load_assets():
    model = pickle.load(open("model/crop_model.pkl", "rb"))
    le = pickle.load(open("model/label_encoder.pkl", "rb"))
    df = pd.read_csv("data/Crop_recommendation.csv")
    return model, le, df

model, le, df = load_assets()

# --- UTILITY FUNCTIONS ---

def get_groq_advice(crop_name, n, p, k, temp, hum):
    """Uses Groq API to get expert advice for the Gradio app."""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"Expert tip for a farmer planting '{crop_name}' in Assam. Context: N:{n}, P:{p}, K:{k}, Temp:{temp}C, Hum:{hum}%. Keep it to 2 short, helpful sentences."
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Expert advice unavailable at the moment."

def get_eda_plot():
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x=['Nitrogen', 'Phosphorus', 'Potassium'], 
                y=[df['N'].mean(), df['P'].mean(), df['K'].mean()], 
                palette="viridis", ax=ax)
    plt.title("Average Nutrient Distribution")
    return fig

# 2. PREDICTION FUNCTION (With Groq Integration)
def predict_crop(n, p, k, ph, rainfall, district):
    temp, hum, status = get_live_weather(district)
    
    if temp:
        # ML Inference
        features = np.array([[n, p, k, temp, hum, ph, rainfall]])
        prediction = model.predict(features)
        crop = le.inverse_transform(prediction)[0]
        
        # Groq Expert Advice
        advice = get_groq_advice(crop, n, p, k, temp, hum)
        
        # Build Styled HTML Output
        output = f"""
        <div style='background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 12px; font-family: sans-serif;'>
            <h2 style='color: #166534; margin: 0 0 10px 0;'>✅ Recommended Crop: {crop.upper()}</h2>
            <p style='color: #374151; font-weight: bold; margin: 0;'>📍 Live Weather ({district}): {temp}°C, {hum}% Humidity</p>
            <hr style='border: 0; border-top: 1px solid #bbf7d0; margin: 15px 0;'>
            <h4 style='color: #166534; margin: 0 0 5px 0;'>💡 Expert AI Advice (Groq):</h4>
            <p style='color: #1f2937; line-height: 1.5; font-style: italic;'>"{advice}"</p>
        </div>
        """
        return output
    else:
        return f"<div style='color: #dc2626; font-weight: bold;'>❌ Weather API Error: {status}</div>"

# 3. GRADIO BLOCKS UI
with gr.Blocks(theme=gr.themes.Soft(), title="Assam Crop Advisor") as demo:
    
    gr.Markdown("# 🌱 AI-Based Crop Advisor for Assam")
    gr.Markdown("Combining **Random Forest ML** with **Groq Llama 3** for smarter farming.")

    # EDA Accordion
    with gr.Accordion("📊 Step 1: Exploratory Data Analysis (EDA)", open=False):
        gr.Dataframe(df.describe().T.head(7), label="Dataset Statistics")
        gr.Plot(get_eda_plot())
    
    gr.Markdown("---")
    
    gr.Markdown("## 🤖 Step 2: Prediction & AI Advice")
    
    with gr.Row():
        with gr.Column():
            n_in = gr.Number(label="Nitrogen (N)", value=80)
            p_in = gr.Number(label="Phosphorus (P)", value=40)
            k_in = gr.Number(label="Potassium (K)", value=40)
            ph_in = gr.Slider(0, 14, label="Soil pH", value=6.5)
            
        with gr.Column():
            rain_in = gr.Number(label="Rainfall (mm)", value=200)
            dist_in = gr.Dropdown(
                ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur", "Nagaon"], 
                label="Assam District",
                value="Guwahati"
            )
            
    predict_btn = gr.Button("🔮 Predict & Get AI Advice", variant="primary")
    
    # Styled Output Area
    result_html = gr.HTML()
    
    # Event Listener
    predict_btn.click(
        fn=predict_crop,
        inputs=[n_in, p_in, k_in, ph_in, rain_in, dist_in],
        outputs=result_html
    )


# 4. LAUNCH
if __name__ == "__main__":
    demo.launch(share=True)
