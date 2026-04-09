"""
Assam Crop Recommendation System
God-Tier Edition: Language Toggle + Fertilizer Prescription + Market Forecaster
"""

import streamlit as st
import requests
import pickle
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import datetime
import urllib3
import urllib.parse
from mappings import soil_properties, season_rainfall
from weather import get_live_weather

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Assam Crop Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADE 6A — ASSAMESE LANGUAGE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

UI_TEXT = {
    "en": {
        "title":           "🌾 Assam Crop Recommendation System",
        "subtitle":        "*AI-powered crop advice tailored to your soil, weather, and location.*",
        "soil_header":     "🌱 Soil & Season Details",
        "soil_type":       "Soil Type",
        "season":          "Current Season",
        "district":        "District / City",
        "input_mode":      "Choose mode",
        "simple":          "👨‍🌾 Simple Mode",
        "advanced":        "🔬 Advanced Mode",
        "display_opts":    "📊 Display Options",
        "show_dash":       "Show environmental dashboard",
        "show_history":    "Show crop history comparison",
        "num_recs":        "Number of recommendations",
        "predict_btn":     "🚀 Get Crop Recommendations",
        "top_rec":         "Top Recommendation",
        "why_crop":        "Why this crop?",
        "confidence":      "Model confidence",
        "top_n_recs":      "Top Recommendations",
        "env_analysis":    "📊 Environmental Analysis",
        "history_title":   "📋 Recommendation History (This Session)",
        "clear_history":   "🗑️ Clear History",
        "export_title":    "🖨️ Export Results",
        "export_desc":     "Download a printable summary of this analysis for field use.",
        "download_pdf":    "📄 Download Official PDF Report",
        "input_summary":   "🔍 View full input summary used for this prediction",
        "fert_title":      "🧪 Fertilizer Prescription",
        "fert_desc":       "Based on your soil's current nutrient levels vs. what this crop needs:",
        "fert_optimal":    "✅ Soil nutrient levels are optimal for this crop!",
        "market_title":    "📈 Market & Economics Forecast",
        "market_price":    "Est. Market Price",
        "market_yield":    "Est. Yield / hectare",
        "market_revenue":  "Est. Gross Revenue",
        "market_cost":     "Est. Input Cost",
        "market_profit":   "Est. Net Profit",
        "market_note":     "Prices based on Assam Mandi averages. Actual prices may vary.",
        "water_need":      "Water need",
        "lang_toggle":     "🌐 Language",
        "location_hdr":    "📍 Location",
        "input_mode_hdr":  "⚙️ Input Mode",
        "caption":         "Built for Assam farmers · v3.0\nPowered by Random Forest ML",
        "fetching":        "Fetching live weather data and running AI analysis…",
        "analysis_done":   "✅ Analysis complete!",
        "model_not_found": "⚠️ Model files not found! Run `train_model.ipynb` first.",
        "weather_error":   "Weather API Error",
        "best_fit":        "Best fit for your soil composition, current weather in",
        "best_fit2":       "and seasonal conditions.",
        "real_photo":      "📸 Real photo",
        "ai_matched":      "The AI matched",
        "based_on":        "based on your soil (pH",
        "live_weather":    "live weather in",
        "exp_rainfall":    "mm expected rainfall.",
        "hist_align":      "These conditions closely align with historical growing data for this crop in Assam.",
        "nitrogen":        "Nitrogen (N)",
        "phosphorus":      "Phosphorus (P)",
        "potassium":       "Potassium (K)",
        "soil_ph":         "Soil pH",
        "rainfall_mm":     "Rainfall (mm)",
        "temperature":     "Temperature (°C)",
        "humidity":        "Humidity (%)",
        "district_lbl":    "District",
        "value":           "Value",
        "pdf_report":      "AI Crop Recommendation Report",
        "pdf_date":        "Date Generated",
        "pdf_location":    "Analyzed Location",
        "pdf_top_crop":    "Top Recommended Crop",
        "pdf_env":         "Environmental & Soil Data Analyzed",
        "pdf_footer":      "This report was generated automatically by the Assam Crop Recommendation System.",
        "pdf_fert":        "Fertilizer Prescription",
        "pdf_market":      "Market & Economics Forecast",
        "add_urea":        "Add Urea",
        "add_dap":         "Add DAP",
        "add_mop":         "Add MOP (Muriate of Potash)",
        "kg_per_ha":       "kg/hectare",
        "no_deficit":      "No amendment needed",
        "per_ha":          "per hectare",
    },
    "as": {
        "title":           "🌾 অসম শস্য পৰামৰ্শ প্ৰণালী",
        "subtitle":        "*আপোনাৰ মাটি, বতৰ আৰু স্থানৰ ওপৰত ভিত্তি কৰি AI-চালিত শস্য পৰামৰ্শ।*",
        "soil_header":     "🌱 মাটি আৰু ঋতুৰ বিৱৰণ",
        "soil_type":       "মাটিৰ প্ৰকাৰ",
        "season":          "বৰ্তমান ঋতু",
        "district":        "জিলা / চহৰ",
        "input_mode":      "মোড বাছক",
        "simple":          "👨‍🌾 সহজ মোড",
        "advanced":        "🔬 উন্নত মোড",
        "display_opts":    "📊 প্ৰদৰ্শন বিকল্প",
        "show_dash":       "পৰিৱেশ ড্যাশব'ৰ্ড দেখুৱাওক",
        "show_history":    "শস্যৰ ইতিহাস তুলনা দেখুৱাওক",
        "num_recs":        "পৰামৰ্শৰ সংখ্যা",
        "predict_btn":     "🚀 শস্যৰ পৰামৰ্শ লওক",
        "top_rec":         "শীৰ্ষ পৰামৰ্শ",
        "why_crop":        "এই শস্য কিয়?",
        "confidence":      "মডেলৰ আত্মবিশ্বাস",
        "top_n_recs":      "শীৰ্ষ পৰামৰ্শসমূহ",
        "env_analysis":    "📊 পৰিৱেশ বিশ্লেষণ",
        "history_title":   "📋 পৰামৰ্শৰ ইতিহাস (এই অধিবেশন)",
        "clear_history":   "🗑️ ইতিহাস মচক",
        "export_title":    "🖨️ ফলাফল ৰপ্তানি কৰক",
        "export_desc":     "এই বিশ্লেষণৰ এটা মুদ্ৰণযোগ্য সাৰাংশ ডাউনলোড কৰক।",
        "download_pdf":    "📄 চৰকাৰী PDF প্ৰতিবেদন ডাউনলোড কৰক",
        "input_summary":   "🔍 এই পূৰ্বানুমানৰ বাবে ব্যৱহৃত সম্পূৰ্ণ ইনপুট সাৰাংশ চাওক",
        "fert_title":      "🧪 সাৰ প্ৰেচক্ৰিপচন",
        "fert_desc":       "আপোনাৰ মাটিৰ বৰ্তমান পুষ্টি স্তৰ বনাম এই শস্যৰ প্ৰয়োজনীয়তা:",
        "fert_optimal":    "✅ এই শস্যৰ বাবে মাটিৰ পুষ্টি স্তৰ সৰ্বোত্তম!",
        "market_title":    "📈 বজাৰ আৰু অৰ্থনীতি পূৰ্বানুমান",
        "market_price":    "আনু. বজাৰ মূল্য",
        "market_yield":    "আনু. উৎপাদন / হেক্টৰ",
        "market_revenue":  "আনু. মুঠ ৰাজহ",
        "market_cost":     "আনু. ইনপুট খৰচ",
        "market_profit":   "আনু. নিট লাভ",
        "market_note":     "মূল্য অসম মণ্ডিৰ গড়ৰ ওপৰত ভিত্তি কৰি। প্ৰকৃত মূল্য ভিন্ন হ'ব পাৰে।",
        "water_need":      "পানীৰ প্ৰয়োজন",
        "lang_toggle":     "🌐 ভাষা",
        "location_hdr":    "📍 স্থান",
        "input_mode_hdr":  "⚙️ ইনপুট মোড",
        "caption":         "অসমৰ কৃষকৰ বাবে নিৰ্মিত · v3.0\nRandom Forest ML দ্বাৰা চালিত",
        "fetching":        "লাইভ বতৰৰ ডেটা আনি AI বিশ্লেষণ চলাইছে…",
        "analysis_done":   "✅ বিশ্লেষণ সম্পূৰ্ণ!",
        "model_not_found": "⚠️ মডেল ফাইল পোৱা নগ'ল! প্ৰথমে `train_model.ipynb` চলাওক।",
        "weather_error":   "বতৰ API ত্ৰুটি",
        "best_fit":        "আপোনাৰ মাটি, বৰ্তমান বতৰ আৰু ঋতু পৰিস্থিতিৰ বাবে সৰ্বোত্তম —",
        "best_fit2":       "",
        "real_photo":      "📸 প্ৰকৃত ফটো",
        "ai_matched":      "AI এ মিলাইছে",
        "based_on":        "আপোনাৰ মাটিৰ ওপৰত ভিত্তি কৰি (pH",
        "live_weather":    "লাইভ বতৰ",
        "exp_rainfall":    "mm আশা কৰা বৃষ্টিপাত।",
        "hist_align":      "এই অৱস্থাসমূহ অসমত এই শস্যৰ ঐতিহাসিক বৃদ্ধিৰ ডেটাৰ সৈতে ঘনিষ্ঠভাৱে মিলে।",
        "nitrogen":        "নাইট্ৰজেন (N)",
        "phosphorus":      "ফছফৰাছ (P)",
        "potassium":       "পটাছিয়াম (K)",
        "soil_ph":         "মাটিৰ pH",
        "rainfall_mm":     "বৃষ্টিপাত (mm)",
        "temperature":     "তাপমাত্ৰা (°C)",
        "humidity":        "আৰ্দ্ৰতা (%)",
        "district_lbl":    "জিলা",
        "value":           "মান",
        "pdf_report":      "AI শস্য পৰামৰ্শ প্ৰতিবেদন",
        "pdf_date":        "উৎপাদনৰ তাৰিখ",
        "pdf_location":    "বিশ্লেষণ কৰা স্থান",
        "pdf_top_crop":    "শীৰ্ষ পৰামৰ্শ কৰা শস্য",
        "pdf_env":         "পৰিৱেশ আৰু মাটিৰ ডেটা বিশ্লেষণ কৰা হৈছে",
        "pdf_footer":      "এই প্ৰতিবেদনটো অসম শস্য পৰামৰ্শ প্ৰণালীৰ দ্বাৰা স্বয়ংক্ৰিয়ভাৱে উৎপন্ন কৰা হৈছিল।",
        "pdf_fert":        "সাৰ প্ৰেচক্ৰিপচন",
        "pdf_market":      "বজাৰ আৰু অৰ্থনীতি পূৰ্বানুমান",
        "add_urea":        "ইউৰিয়া যোগ কৰক",
        "add_dap":         "DAP যোগ কৰক",
        "add_mop":         "MOP যোগ কৰক",
        "kg_per_ha":       "কেজি/হেক্টৰ",
        "no_deficit":      "সংশোধনৰ প্ৰয়োজন নাই",
        "per_ha":          "প্ৰতি হেক্টৰ",
    }
}

def T(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return UI_TEXT.get(lang, UI_TEXT["en"]).get(key, key)

# ═══════════════════════════════════════════════════════════════════════════════
# CAMERA CROP RECOGNITION
# ═══════════════════════════════════════════════════════════════════════════════

import google.generativeai as genai, base64, json, re
import streamlit as st
import streamlit.components.v1 as components

def identify_crop_from_image(img_bytes: bytes) -> dict:
    try:
        # Configure Gemini
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        # Send image + prompt
        response = model.generate_content([
            {
                "mime_type": "image/jpeg",
                "data": img_bytes
            },
            """You are an agricultural expert for Assam, India.
Identify the crop in this image and check for disease.

Reply ONLY in JSON:
{"crop_key": "rice", "display_name": "Rice", "disease": null, "confidence": 90, "notes": "Healthy plant"}"""
        ])

        # Clean response
        raw = response.text
        clean = re.sub(r"```json|```", "", raw).strip()

        return json.loads(clean)

    except Exception as e:
        return {
            "crop_key": "unknown",
            "display_name": "Unknown",
            "disease": None,
            "confidence": 0,
            "notes": str(e)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SPEAK ALOUD (TTS)
# ═══════════════════════════════════════════════════════════════════════════════

def build_tts_summary(crop_name, fert, market, lang="en") -> str:
    if lang == "as":
        text = (f"শীৰ্ষ শস্য: {crop_name}। "
                f"ইউৰিয়া {fert['urea_kg']} কেজি, DAP {fert['dap_kg']} কেজি প্ৰয়োগ কৰক। "
                f"অনুমানিত লাভ প্ৰতি হেক্টৰত {market['net_profit']:,} টকা।")
    else:
        text = (f"Top recommended crop: {crop_name}. "
                f"Apply {fert['urea_kg']} kg Urea, {fert['dap_kg']} kg DAP, "
                f"{fert['mop_kg']} kg MOP per hectare. "
                f"Estimated net profit: Rupees {market['net_profit']:,} per hectare.")
    return text


def render_tts_player(text: str, lang: str = "en") -> None:
    lang_code = "as-IN" if lang == "as" else "en-IN"
    escaped = text.replace("'", "\\'").replace("\n", " ")
    html = f"""
    <div style="display:flex;align-items:center;gap:10px;padding:.6rem 1rem;
         background:rgba(0,0,0,.04);border-radius:8px;font-size:13px;">
      <button onclick="speak()" style="padding:6px 14px;border-radius:6px;
              border:1px solid #aaa;cursor:pointer;background:white;">&#9654; Play</button>
      <button onclick="window.speechSynthesis.cancel()" style="padding:6px 14px;
              border-radius:6px;border:1px solid #aaa;cursor:pointer;background:white;">&#9632; Stop</button>
      <span style="opacity:.6;flex:1;overflow:hidden;white-space:nowrap;
                   text-overflow:ellipsis;">{text[:80]}…</span>
    </div>
    <script>
    function speak() {{
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance('{escaped}');
      u.lang = '{lang_code}';
      u.rate = 0.9;
      window.speechSynthesis.speak(u);
    }}
    </script>
    """
    components.html(html, height=60)
# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADE 6B — FERTILIZER PRESCRIPTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

# Optimal NPK requirements per crop (kg/hectare)
# Values sourced from ICAR & Assam Agriculture Department recommendations
CROP_NPK_REQUIREMENTS: dict[str, dict] = {
    "rice":          {"N": 80,  "P": 40,  "K": 40},
    "wheat":         {"N": 120, "P": 60,  "K": 40},
    "maize":         {"N": 120, "P": 60,  "K": 60},
    "jute":          {"N": 60,  "P": 30,  "K": 30},
    "assam_tea":     {"N": 150, "P": 30,  "K": 50},
    "mustard":       {"N": 80,  "P": 40,  "K": 40},
    "sugarcane":     {"N": 250, "P": 60,  "K": 120},
    "cotton":        {"N": 100, "P": 50,  "K": 50},
    "banana":        {"N": 200, "P": 60,  "K": 300},
    "mango":         {"N": 100, "P": 50,  "K": 100},
    "chickpea":      {"N": 20,  "P": 60,  "K": 30},
    "lentil":        {"N": 20,  "P": 40,  "K": 20},
    "papaya":        {"N": 200, "P": 200, "K": 250},
    "coconut":       {"N": 100, "P": 40,  "K": 200},
    "pomegranate":   {"N": 60,  "P": 60,  "K": 60},
    "grapes":        {"N": 100, "P": 60,  "K": 80},
    "watermelon":    {"N": 80,  "P": 40,  "K": 60},
    "muskmelon":     {"N": 80,  "P": 40,  "K": 60},
    "orange":        {"N": 100, "P": 50,  "K": 100},
    "apple":         {"N": 70,  "P": 35,  "K": 70},
    "mungbean":      {"N": 20,  "P": 40,  "K": 20},
    "mothbeans":     {"N": 20,  "P": 40,  "K": 20},
    "pigeonpeas":    {"N": 20,  "P": 50,  "K": 20},
    "kidneybeans":   {"N": 20,  "P": 60,  "K": 30},
    "blackgram":     {"N": 20,  "P": 40,  "K": 20},
    "coffee":        {"N": 150, "P": 50,  "K": 100},
    "joha_rice":     {"N": 60,  "P": 30,  "K": 30},
    "joha_rice72":   {"N": 60,  "P": 30,  "K": 30},
    "bao_rice":      {"N": 50,  "P": 25,  "K": 25},
    "bora_rice":     {"N": 70,  "P": 35,  "K": 35},
    "chokuwa_rice":  {"N": 55,  "P": 28,  "K": 28},
    "komal_saul":    {"N": 50,  "P": 25,  "K": 25},
    "xaaj_rice":     {"N": 60,  "P": 30,  "K": 30},
    "apong_rice":    {"N": 60,  "P": 30,  "K": 30},
    "bhut_jolokia":  {"N": 100, "P": 60,  "K": 80},
    "kaji_nemu":     {"N": 80,  "P": 40,  "K": 60},
    "ou_tenga":      {"N": 60,  "P": 30,  "K": 40},
    "thekera":       {"N": 50,  "P": 25,  "K": 30},
    "amlokhi":       {"N": 60,  "P": 30,  "K": 50},
    "bogori":        {"N": 50,  "P": 25,  "K": 30},
    "leteku":        {"N": 80,  "P": 40,  "K": 60},
    "jalpai":        {"N": 60,  "P": 30,  "K": 40},
    "areca_nut":     {"N": 100, "P": 40,  "K": 140},
    "betel_leaf":    {"N": 80,  "P": 40,  "K": 60},
    "kola_banana":   {"N": 180, "P": 60,  "K": 280},
    "lai_xaak":      {"N": 60,  "P": 30,  "K": 30},
    "kosu":          {"N": 100, "P": 50,  "K": 100},
    "dhekia_xaak":   {"N": 40,  "P": 20,  "K": 20},
    "manimuni":      {"N": 30,  "P": 15,  "K": 15},
    "local_brinjal": {"N": 100, "P": 50,  "K": 60},
    "local_pumpkin": {"N": 80,  "P": 60,  "K": 80},
    "local_beans":   {"N": 20,  "P": 60,  "K": 30},
    "bamboo_shoot":  {"N": 60,  "P": 30,  "K": 40},
}

# Fertilizer conversion factors (kg of fertilizer to supply 1 kg of nutrient)
# Urea = 46% N,  DAP = 18% N + 46% P,  MOP = 60% K
UREA_FACTOR = 1 / 0.46   # kg Urea per kg N
DAP_N_FACTOR = 0.18       # kg N per kg DAP
DAP_P_FACTOR = 1 / 0.46  # kg DAP per kg P
MOP_FACTOR   = 1 / 0.60  # kg MOP per kg K

def calculate_fertilizer_prescription(crop_key: str, actual_N: float, actual_P: float, actual_K: float) -> dict:
    """
    Returns dict with deficit values and fertilizer amounts in kg/hectare.
    Uses standard agronomic formula:
      - P deficit → apply DAP first (it also supplies some N)
      - Remaining N deficit → apply Urea
      - K deficit → apply MOP
    """
    req = CROP_NPK_REQUIREMENTS.get(crop_key.lower(),
                                    {"N": 80, "P": 40, "K": 40})
    deficit_N = max(0, req["N"] - actual_N)
    deficit_P = max(0, req["P"] - actual_P)
    deficit_K = max(0, req["K"] - actual_K)

    # Step 1: DAP to cover P deficit (also provides some N)
    dap_kg      = deficit_P * DAP_P_FACTOR
    n_from_dap  = dap_kg * DAP_N_FACTOR
    remaining_N = max(0, deficit_N - n_from_dap)

    # Step 2: Urea to cover remaining N
    urea_kg = remaining_N * UREA_FACTOR

    # Step 3: MOP for K
    mop_kg = deficit_K * MOP_FACTOR

    return {
        "required":   req,
        "deficit_N":  round(deficit_N),
        "deficit_P":  round(deficit_P),
        "deficit_K":  round(deficit_K),
        "urea_kg":    round(urea_kg),
        "dap_kg":     round(dap_kg),
        "mop_kg":     round(mop_kg),
        "all_optimal": deficit_N == 0 and deficit_P == 0 and deficit_K == 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADE 6C — MARKET & ECONOMICS FORECASTER
# ═══════════════════════════════════════════════════════════════════════════════

# Assam Mandi average prices (INR per quintal = 100 kg)
# Source: Agmarknet / data.gov.in historical averages for Assam (2024-25)
# Yield in quintals per hectare (ICAR Assam averages)
MARKET_DATA: dict[str, dict] = {
    "rice":          {"price_per_q": 2200, "yield_q_ha": 25,  "input_cost": 25000},
    "wheat":         {"price_per_q": 2275, "yield_q_ha": 30,  "input_cost": 22000},
    "maize":         {"price_per_q": 1850, "yield_q_ha": 35,  "input_cost": 18000},
    "jute":          {"price_per_q": 5500, "yield_q_ha": 20,  "input_cost": 20000},
    "assam_tea":     {"price_per_q": 15000,"yield_q_ha": 18,  "input_cost": 80000},
    "mustard":       {"price_per_q": 5650, "yield_q_ha": 10,  "input_cost": 15000},
    "sugarcane":     {"price_per_q": 315,  "yield_q_ha": 600, "input_cost": 40000},
    "cotton":        {"price_per_q": 6600, "yield_q_ha": 15,  "input_cost": 35000},
    "banana":        {"price_per_q": 1500, "yield_q_ha": 200, "input_cost": 45000},
    "mango":         {"price_per_q": 3000, "yield_q_ha": 80,  "input_cost": 30000},
    "chickpea":      {"price_per_q": 5440, "yield_q_ha": 12,  "input_cost": 18000},
    "lentil":        {"price_per_q": 6000, "yield_q_ha": 10,  "input_cost": 15000},
    "papaya":        {"price_per_q": 800,  "yield_q_ha": 250, "input_cost": 35000},
    "coconut":       {"price_per_q": 2500, "yield_q_ha": 120, "input_cost": 25000},
    "pomegranate":   {"price_per_q": 8000, "yield_q_ha": 80,  "input_cost": 40000},
    "grapes":        {"price_per_q": 6000, "yield_q_ha": 100, "input_cost": 50000},
    "watermelon":    {"price_per_q": 600,  "yield_q_ha": 250, "input_cost": 20000},
    "muskmelon":     {"price_per_q": 1200, "yield_q_ha": 150, "input_cost": 20000},
    "orange":        {"price_per_q": 4000, "yield_q_ha": 100, "input_cost": 35000},
    "apple":         {"price_per_q": 8000, "yield_q_ha": 80,  "input_cost": 45000},
    "mungbean":      {"price_per_q": 7755, "yield_q_ha": 8,   "input_cost": 12000},
    "mothbeans":     {"price_per_q": 6000, "yield_q_ha": 7,   "input_cost": 10000},
    "pigeonpeas":    {"price_per_q": 7000, "yield_q_ha": 10,  "input_cost": 12000},
    "kidneybeans":   {"price_per_q": 9000, "yield_q_ha": 12,  "input_cost": 18000},
    "blackgram":     {"price_per_q": 7400, "yield_q_ha": 8,   "input_cost": 12000},
    "coffee":        {"price_per_q": 18000,"yield_q_ha": 8,   "input_cost": 50000},
    "joha_rice":     {"price_per_q": 6000, "yield_q_ha": 18,  "input_cost": 22000},
    "joha_rice72":   {"price_per_q": 5500, "yield_q_ha": 20,  "input_cost": 22000},
    "bao_rice":      {"price_per_q": 3500, "yield_q_ha": 20,  "input_cost": 20000},
    "bora_rice":     {"price_per_q": 4500, "yield_q_ha": 18,  "input_cost": 20000},
    "chokuwa_rice":  {"price_per_q": 5000, "yield_q_ha": 18,  "input_cost": 20000},
    "komal_saul":    {"price_per_q": 7000, "yield_q_ha": 15,  "input_cost": 22000},
    "xaaj_rice":     {"price_per_q": 4000, "yield_q_ha": 20,  "input_cost": 20000},
    "apong_rice":    {"price_per_q": 4000, "yield_q_ha": 20,  "input_cost": 20000},
    "bhut_jolokia":  {"price_per_q": 25000,"yield_q_ha": 12,  "input_cost": 30000},
    "kaji_nemu":     {"price_per_q": 4000, "yield_q_ha": 80,  "input_cost": 20000},
    "ou_tenga":      {"price_per_q": 2000, "yield_q_ha": 60,  "input_cost": 15000},
    "thekera":       {"price_per_q": 3000, "yield_q_ha": 40,  "input_cost": 15000},
    "amlokhi":       {"price_per_q": 3500, "yield_q_ha": 60,  "input_cost": 20000},
    "bogori":        {"price_per_q": 2500, "yield_q_ha": 50,  "input_cost": 15000},
    "leteku":        {"price_per_q": 5000, "yield_q_ha": 50,  "input_cost": 20000},
    "jalpai":        {"price_per_q": 2000, "yield_q_ha": 40,  "input_cost": 15000},
    "areca_nut":     {"price_per_q": 35000,"yield_q_ha": 15,  "input_cost": 40000},
    "betel_leaf":    {"price_per_q": 8000, "yield_q_ha": 30,  "input_cost": 25000},
    "kola_banana":   {"price_per_q": 2000, "yield_q_ha": 180, "input_cost": 40000},
    "lai_xaak":      {"price_per_q": 800,  "yield_q_ha": 80,  "input_cost": 10000},
    "kosu":          {"price_per_q": 1200, "yield_q_ha": 100, "input_cost": 15000},
    "dhekia_xaak":   {"price_per_q": 1500, "yield_q_ha": 30,  "input_cost": 8000},
    "manimuni":      {"price_per_q": 2000, "yield_q_ha": 40,  "input_cost": 8000},
    "local_brinjal": {"price_per_q": 1500, "yield_q_ha": 150, "input_cost": 20000},
    "local_pumpkin": {"price_per_q": 800,  "yield_q_ha": 200, "input_cost": 15000},
    "local_beans":   {"price_per_q": 4000, "yield_q_ha": 20,  "input_cost": 15000},
    "bamboo_shoot":  {"price_per_q": 3000, "yield_q_ha": 50,  "input_cost": 10000},
}

def get_market_forecast(crop_key: str) -> dict:
    data        = MARKET_DATA.get(crop_key.lower(), {"price_per_q": 2000, "yield_q_ha": 20, "input_cost": 20000})
    revenue     = data["price_per_q"] * data["yield_q_ha"]
    net_profit  = revenue - data["input_cost"]
    roi_pct     = (net_profit / data["input_cost"]) * 100 if data["input_cost"] > 0 else 0
    return {
        "price_per_q":  data["price_per_q"],
        "yield_q_ha":   data["yield_q_ha"],
        "input_cost":   data["input_cost"],
        "revenue":      revenue,
        "net_profit":   net_profit,
        "roi_pct":      round(roi_pct, 1),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PDF REPORT GENERATOR (Updated for all 3 upgrades)
# ═══════════════════════════════════════════════════════════════════════════════

import os, urllib.request

def _ensure_unicode_font() -> str:
    """
    Downloads NotoSans-Regular.ttf once into the project folder.
    Returns the file path. Safe to call every time — skips if already present.
    """
    font_path = "NotoSans-Regular.ttf"
    if not os.path.exists(font_path):
        url = (
            "https://github.com/googlefonts/noto-fonts/raw/main/"
            "hinted/ttf/NotoSans/NotoSans-Regular.ttf"
        )
        urllib.request.urlretrieve(url, font_path)
    return font_path


def create_pdf_report(district, crop_name, confidence, temp, humidity, ph,
                      rainfall, N, P, K, fert: dict, market: dict, lang: str = "en") -> bytes:
    t = UI_TEXT.get(lang, UI_TEXT["en"])
    pdf = FPDF()
    pdf.add_page()

    # ── Font setup ────────────────────────────────────────────────────────────
    # Assamese needs a Unicode TTF font. English can use built-in Helvetica.
    # ── Font setup ────────────────────────────────────────────────────────────
    if lang == "as":
        font_path = _ensure_unicode_font()
        pdf.add_font("NotoSans", style="",  fname=font_path)
        pdf.add_font("NotoSans", style="B", fname=font_path)
        FONT_NORMAL = "NotoSans"
        FONT_BOLD   = "NotoSans"
    else:
        font_path = "DejaVuSans.ttf"
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        FONT_NORMAL = "DejaVu"
        FONT_BOLD   = "DejaVu"

    def set_normal(size=12):
        pdf.set_font(FONT_NORMAL, size=size)

    def set_bold(size=12):
        pdf.set_font(FONT_BOLD, style="B" if lang == "en" else "", size=size)

    # ── Header ────────────────────────────────────────────────────────────────
    set_bold(20)
    pdf.set_text_color(46, 139, 87)
    pdf.cell(0, 15, t["pdf_report"], ln=True, align='C')
    pdf.ln(3)

    # ── General info ──────────────────────────────────────────────────────────
    set_normal(12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"{t['pdf_date']}: {datetime.date.today().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(0, 10, f"{t['pdf_location']}: {district.title()}, Assam", ln=True)
    pdf.ln(3)

    # ── Top recommendation ────────────────────────────────────────────────────
    set_bold(14)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, f"{t['pdf_top_crop']}: {crop_name} ({confidence:.1f}% AI Confidence)", ln=True)
    pdf.ln(3)

    # ── Environmental data ────────────────────────────────────────────────────
    set_bold(12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"{t['pdf_env']}:", ln=True)
    set_normal(12)
    pdf.cell(0, 8, f"  - {t['temperature']}: {temp} C", ln=True)
    pdf.cell(0, 8, f"  - {t['humidity']}: {humidity} %", ln=True)
    pdf.cell(0, 8, f"  - {t['rainfall_mm']}: {rainfall} mm", ln=True)
    pdf.cell(0, 8, f"  - {t['soil_ph']}: {ph}", ln=True)
    pdf.cell(0, 8, f"  - N: {N}  |  P: {P}  |  K: {K}", ln=True)
    pdf.ln(4)

    # ── Fertilizer prescription ───────────────────────────────────────────────
    set_bold(12)
    pdf.set_text_color(139, 69, 19)
    pdf.cell(0, 10, f"{t['pdf_fert']}:", ln=True)
    set_normal(12)
    pdf.set_text_color(0, 0, 0)
    if fert["all_optimal"]:
        pdf.cell(0, 8, f"  {t['fert_optimal']}", ln=True)
    else:
        if fert["urea_kg"] > 0:
            pdf.cell(0, 8, f"  - {t['add_urea']}: {fert['urea_kg']} {t['kg_per_ha']}", ln=True)
        if fert["dap_kg"] > 0:
            pdf.cell(0, 8, f"  - {t['add_dap']}: {fert['dap_kg']} {t['kg_per_ha']}", ln=True)
        if fert["mop_kg"] > 0:
            pdf.cell(0, 8, f"  - {t['add_mop']}: {fert['mop_kg']} {t['kg_per_ha']}", ln=True)
    pdf.ln(4)

    # ── Market forecast ───────────────────────────────────────────────────────
    set_bold(12)
    pdf.set_text_color(0, 70, 140)
    pdf.cell(0, 10, f"{t['pdf_market']}:", ln=True)
    set_normal(12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"  - {t['market_price']}: Rs. {market['price_per_q']:,} / quintal", ln=True)
    pdf.cell(0, 8, f"  - {t['market_yield']}: {market['yield_q_ha']} quintals", ln=True)
    pdf.cell(0, 8, f"  - {t['market_revenue']}: Rs. {market['revenue']:,}", ln=True)
    pdf.cell(0, 8, f"  - {t['market_cost']}: Rs. {market['input_cost']:,}", ln=True)
    pdf.cell(0, 8, f"  - {t['market_profit']}: Rs. {market['net_profit']:,}  (ROI: {market['roi_pct']}%)", ln=True)
    pdf.ln(10)

    # ── Footer ────────────────────────────────────────────────────────────────
    set_normal(10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, t["pdf_footer"], align='C')

    return bytes(pdf.output())


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE FETCHING (unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

_IMG_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
}

_SKIP_KEYWORDS = [
    "icon", "flag", "map", "logo", "diagram", "svg", "symbol",
    "coat", "blank", "book", "cover", "notebook", "paper",
    "text", "stamp", "poster", "label", "chart", "graph",
    "schema", "drawing", "illustration", "clipart", "cartoon",
    "pattern", "background", "wallpaper", "texture", "sample",
    "template", "placeholder", "generic", "default", "unknown",
    "wiki", "commons", "wikipedia",
]
_VALID_EXTS = (".jpg", ".jpeg", ".png", ".webp")

_CROP_WIKI_TITLES = {
    "rice": "Rice", "wheat": "Wheat", "maize": "Maize", "jute": "Jute",
    "assam_tea": "Assam_tea", "coffee": "Coffea", "mustard": "Mustard_plant",
    "sugarcane": "Sugarcane", "cotton": "Cotton", "banana": "Banana",
    "mango": "Mango", "chickpea": "Chickpea", "lentil": "Lentil",
    "papaya": "Papaya", "coconut": "Coconut", "pomegranate": "Pomegranate",
    "grapes": "Grape", "watermelon": "Watermelon", "muskmelon": "Muskmelon",
    "orange": "Orange_(fruit)", "apple": "Apple", "mungbean": "Mung_bean",
    "mothbeans": "Moth_bean", "pigeonpeas": "Pigeon_pea",
    "kidneybeans": "Kidney_bean", "blackgram": "Vigna_mungo",
    "joha_rice": "Joha_rice", "joha_rice72": "Joha_rice",
    "bao_rice": "Bao_rice", "bora_rice": "Glutinous_rice",
    "chokuwa_rice": "Chokuwa_rice", "komal_saul": "Komal_saul",
    "xaaj_rice": "Xaj_(drink)", "apong_rice": "Apong",
    "bhut_jolokia": "Bhut_jolokia", "kaji_nemu": "Kaji_Nemu",
    "ou_tenga": "Elephant_apple", "thekera": "Garcinia_pedunculata",
    "amlokhi": "Phyllanthus_emblica", "bogori": "Ziziphus_mauritiana",
    "leteku": "Baccaurea_ramiflora", "jalpai": "Elaeocarpus_floribundus",
    "areca_nut": "Areca_nut", "betel_leaf": "Betel", "kola_banana": "Banana",
    "lai_xaak": "Brassica_juncea", "kosu": "Colocasia_esculenta",
    "dhekia_xaak": "Diplazium_esculentum", "manimuni": "Centella_asiatica",
    "local_brinjal": "Brinjal", "local_pumpkin": "Pumpkin",
    "local_beans": "Bean", "bamboo_shoot": "Bamboo_shoot",
}

_CROP_DISPLAY_NAMES = {
    "joha_rice": "Joha Rice", "joha_rice72": "Joha Rice (72)",
    "bao_rice": "Bao Rice", "bora_rice": "Bora Rice (Glutinous)",
    "chokuwa_rice": "Chokuwa Rice", "komal_saul": "Komal Saul (Soft Rice)",
    "xaaj_rice": "Xaaj Rice", "apong_rice": "Apong Rice",
    "bhut_jolokia": "Bhut Jolokia (Ghost Pepper)",
    "kaji_nemu": "Kaji Nemu (Assam Lemon)",
    "ou_tenga": "Ou Tenga (Elephant Apple)", "thekera": "Thekera",
    "amlokhi": "Amlokhi (Indian Gooseberry)",
    "bogori": "Bogori (Indian Jujube)", "leteku": "Leteku",
    "jalpai": "Jalpai (Indian Olive)", "areca_nut": "Areca Nut (Tamul)",
    "betel_leaf": "Betel Leaf (Pan)", "kola_banana": "Kola Banana",
    "lai_xaak": "Lai Xaak (Mustard Greens)", "kosu": "Kosu (Taro)",
    "dhekia_xaak": "Dhekia Xaak (Edible Fern)",
    "manimuni": "Manimuni (Pennywort)", "local_brinjal": "Local Brinjal",
    "local_pumpkin": "Local Pumpkin", "local_beans": "Local Beans",
    "bamboo_shoot": "Bamboo Shoot", "assam_tea": "Assam Tea",
}

def get_display_name(crop_key: str) -> str:
    if crop_key in _CROP_DISPLAY_NAMES:
        return _CROP_DISPLAY_NAMES[crop_key]
    return crop_key.replace("_", " ").title()

def _get_image_bytes(url: str):
    try:
        r = requests.get(url, headers=_IMG_HEADERS, timeout=10,
                         verify=False, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "image" in ct and len(r.content) > 10_000:
            return r.content
    except Exception:
        pass
    return None

def _url_is_clean(url: str) -> bool:
    url_lower = url.lower()
    if not any(url_lower.endswith(ext) or (ext + "?") in url_lower for ext in _VALID_EXTS):
        return False
    return not any(kw in url_lower for kw in _SKIP_KEYWORDS)

def _try_wikipedia_infobox(crop_key: str):
    title = _CROP_WIKI_TITLES.get(crop_key.lower())
    if not title:
        return None
    try:
        api = (f"https://en.wikipedia.org/w/api.php"
               f"?action=query&titles={title}&prop=pageimages"
               "&pithumbsize=600&format=json&origin=*")
        r = requests.get(api, headers={"User-Agent": "AssamCropRecommender/2.0"},
                         timeout=10, verify=False)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for page in pages.values():
                thumb = page.get("thumbnail", {}).get("source", "")
                if thumb:
                    img = _get_image_bytes(thumb)
                    if img:
                        return img
    except Exception:
        pass
    return None

def _try_wikimedia_search(crop_name: str):
    query = urllib.parse.quote(f"{crop_name} crop plant field")
    try:
        api = (f"https://commons.wikimedia.org/w/api.php"
               f"?action=query&generator=search&gsrnamespace=6&gsrsearch={query}"
               "&prop=imageinfo&iiprop=url&iiurlwidth=600"
               "&format=json&origin=*&gsrlimit=25")
        r = requests.get(api, headers={"User-Agent": "AssamCropRecommender/2.0"},
                         timeout=10, verify=False)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for page in pages.values():
                info  = page.get("imageinfo", [{}])[0]
                thumb = info.get("thumburl") or info.get("url", "")
                if thumb and _url_is_clean(thumb):
                    img = _get_image_bytes(thumb)
                    if img:
                        return img
    except Exception:
        pass
    return None

def _make_placeholder_png(crop_name: str) -> bytes:
    from PIL import ImageDraw, ImageFont
    W, H = 800, 600
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)],
                  fill=(int(26+(45-26)*t), int(71+(106-71)*t), int(42+(79-42)*t)))
    label    = crop_name.replace("_", " ").title()
    initials = "".join(w[0].upper() for w in label.split()[:2])
    try:
        fb = ImageFont.truetype("arial.ttf", 80)
        fm = ImageFont.truetype("arial.ttf", 52)
        fs = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        fb = fm = fs = ImageFont.load_default()
    draw.text((W//2, H//2-80), initials, font=fb, fill=(255,255,255,30), anchor="mm")
    draw.text((W//2, H//2+20), label,    font=fm, fill=(255,255,255),    anchor="mm")
    draw.text((W//2, H//2+90), "No photo available", font=fs, fill=(180,220,180), anchor="mm")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_data(ttl=86_400, show_spinner=False)
def fetch_crop_image(crop_name: str) -> tuple:
    crop_key = crop_name.lower().replace(" ", "_")
    img = _try_wikipedia_infobox(crop_key)
    if img:
        return img, True
    img = _try_wikimedia_search(crop_name)
    if img:
        return img, True
    return _make_placeholder_png(crop_name), False


# ─── Model Loading ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_models():
    model   = pickle.load(open("model/crop_model.pkl",    "rb"))
    encoder = pickle.load(open("model/label_encoder.pkl", "rb"))
    return model, encoder


# ─── Crop Info ────────────────────────────────────────────────────────────────
CROP_INFO: dict[str, dict] = {
    "rice":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "wheat":{"season":"Rabi (Nov-Apr)","water":"Medium","icon":"🌿"},
    "maize":{"season":"Kharif / Rabi","water":"Medium","icon":"🌽"},
    "jute":{"season":"Kharif (Mar-Jul)","water":"High","icon":"🌱"},
    "assam_tea":{"season":"Year-round","water":"High","icon":"🍵"},
    "mustard":{"season":"Rabi (Oct-Mar)","water":"Low","icon":"🌼"},
    "sugarcane":{"season":"Year-round","water":"High","icon":"🎋"},
    "cotton":{"season":"Kharif (Apr-Nov)","water":"Medium","icon":"☁️"},
    "banana":{"season":"Year-round","water":"Medium","icon":"🍌"},
    "mango":{"season":"Summer (Mar-Jun)","water":"Low","icon":"🥭"},
    "chickpea":{"season":"Rabi (Oct-Mar)","water":"Low","icon":"🫘"},
    "lentil":{"season":"Rabi (Oct-Mar)","water":"Low","icon":"🫘"},
    "papaya":{"season":"Year-round","water":"Medium","icon":"🍈"},
    "coconut":{"season":"Year-round","water":"High","icon":"🥥"},
    "pomegranate":{"season":"Summer / Winter","water":"Low","icon":"🍎"},
    "grapes":{"season":"Winter (Oct-Feb)","water":"Medium","icon":"🍇"},
    "watermelon":{"season":"Summer (Mar-Jun)","water":"Low","icon":"🍉"},
    "muskmelon":{"season":"Summer (Feb-May)","water":"Low","icon":"🍈"},
    "orange":{"season":"Winter (Dec-Feb)","water":"Medium","icon":"🍊"},
    "apple":{"season":"Summer (Jun-Sep)","water":"Medium","icon":"🍎"},
    "mungbean":{"season":"Kharif / Summer","water":"Low","icon":"🫘"},
    "mothbeans":{"season":"Kharif (Jun-Sep)","water":"Low","icon":"🫘"},
    "pigeonpeas":{"season":"Kharif (Jun-Nov)","water":"Low","icon":"🫘"},
    "kidneybeans":{"season":"Kharif (Jun-Sep)","water":"Medium","icon":"🫘"},
    "blackgram":{"season":"Kharif / Rabi","water":"Low","icon":"🫘"},
    "coffee":{"season":"Year-round","water":"Medium","icon":"☕"},
    "joha_rice":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "joha_rice72":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "bao_rice":{"season":"Kharif (Jun-Dec)","water":"High","icon":"🌾"},
    "bora_rice":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "chokuwa_rice":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "komal_saul":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "xaaj_rice":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "apong_rice":{"season":"Kharif (Jun-Nov)","water":"High","icon":"🌾"},
    "bhut_jolokia":{"season":"Kharif (Jul-Oct)","water":"Medium","icon":"🌶️"},
    "kaji_nemu":{"season":"Year-round","water":"Medium","icon":"🍋"},
    "ou_tenga":{"season":"Monsoon (Jun-Sep)","water":"Medium","icon":"🍏"},
    "thekera":{"season":"Monsoon (Jun-Sep)","water":"Medium","icon":"🍋"},
    "amlokhi":{"season":"Rabi (Oct-Feb)","water":"Low","icon":"🟢"},
    "bogori":{"season":"Winter (Oct-Jan)","water":"Low","icon":"🫐"},
    "leteku":{"season":"Summer (Apr-Jun)","water":"Medium","icon":"🍇"},
    "jalpai":{"season":"Monsoon (Jul-Sep)","water":"Medium","icon":"🫒"},
    "areca_nut":{"season":"Year-round","water":"High","icon":"🌴"},
    "betel_leaf":{"season":"Year-round","water":"High","icon":"🍃"},
    "kola_banana":{"season":"Year-round","water":"Medium","icon":"🍌"},
    "lai_xaak":{"season":"Rabi (Oct-Feb)","water":"Medium","icon":"🥬"},
    "kosu":{"season":"Year-round","water":"High","icon":"🌿"},
    "dhekia_xaak":{"season":"Monsoon (Jun-Sep)","water":"High","icon":"🌿"},
    "manimuni":{"season":"Year-round","water":"Medium","icon":"🌿"},
    "local_brinjal":{"season":"Year-round","water":"Medium","icon":"🍆"},
    "local_pumpkin":{"season":"Kharif (Jun-Oct)","water":"Medium","icon":"🎃"},
    "local_beans":{"season":"Kharif / Rabi","water":"Medium","icon":"🫘"},
    "bamboo_shoot":{"season":"Monsoon (Jun-Aug)","water":"High","icon":"🎍"},
}

def get_crop_info(crop_key: str) -> dict:
    return CROP_INFO.get(crop_key.lower(), {"season": "—", "water": "—", "icon": "🌱"})


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

# Language must be initialised before sidebar renders
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

with st.sidebar:
    st.image("https://placehold.co/300x80/1a472a/white?text=Assam+Crop+Advisor",
             use_container_width=True)

    # ── UPGRADE 6A: Language Toggle ───────────────────────────────────────────
    lang_choice = st.radio(
        T("lang_toggle"),
        options=["en", "as"],
        format_func=lambda x: "🇬🇧 English" if x == "en" else "🇮🇳 অসমীয়া",
        horizontal=True,
        key="lang",
    )

    st.markdown("---")
    st.markdown("---")

    # ── Camera Crop Recognition ──────────────────────────────────────────────
    st.markdown("### 📷 Identify Crop from Photo")
    cam_img = st.camera_input("Take a photo") or st.file_uploader(
        "Or upload image", type=["jpg","jpeg","png","webp"], key="cam_upload")

    if cam_img:
        with st.spinner("Identifying crop..."):
            try:
                result = identify_crop_from_image(cam_img.getvalue())
                st.success(f"Detected: **{result['display_name']}** ({result['confidence']}% confidence)")
                if result.get("disease"):
                    st.warning(f"⚠️ Disease detected: {result['disease']}\n\n{result.get('notes','')}")
                else:
                    st.info(f"📝 {result.get('notes', 'No disease found.')}")
                st.session_state["detected_crop"] = result["crop_key"]
            except Exception as e:
                st.error(f"Could not identify crop: {e}")

    st.markdown("---")
    st.caption(T("caption"))

    st.markdown(f'<div class="sidebar-section"><h4>{T("location_hdr")}</h4>', unsafe_allow_html=True)
    district = st.text_input(T("district"), value="Guwahati",
                              help="Used to fetch live temperature & humidity")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div class="sidebar-section"><h4>{T("input_mode_hdr")}</h4>', unsafe_allow_html=True)
    input_mode = st.radio(T("input_mode"), [T("simple"), T("advanced")])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div class="sidebar-section"><h4>{T("display_opts")}</h4>', unsafe_allow_html=True)
    show_dashboard = st.toggle(T("show_dash"),    value=True)
    show_history   = st.toggle(T("show_history"), value=False)
    top_n          = st.slider(T("num_recs"), 3, 7, 3)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption(T("caption"))


# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .crop-card {
        background: linear-gradient(135deg, #1a472a 0%, #2d6a4f 100%);
        border-radius: 16px; padding: 1.5rem 2rem; color: white; margin: 1rem 0;
    }
    .crop-card h2 { margin: 0 0 .25rem 0; font-size: 2rem; }
    .crop-card p  { margin: 0; opacity: .85; font-size: .95rem; }
    .metric-pill {
        display: inline-flex; align-items: center; gap: .4rem;
        background: rgba(46,139,87,.12); border: 1px solid rgba(46,139,87,.25);
        border-radius: 999px; padding: .35rem .9rem; font-size: .85rem; font-weight: 500;
    }
    .fert-card {
        background: rgba(139,69,19,.06); border-left: 4px solid #8B4513;
        border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin: .5rem 0;
    }
    .market-card {
        background: rgba(0,70,140,.06); border-left: 4px solid #00468c;
        border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin: .5rem 0;
    }
    .alert-banner {
        border-left: 4px solid #f0a500; background: rgba(240,165,0,.08);
        border-radius: 0 8px 8px 0; padding: .75rem 1rem; font-size: .9rem;
    }
    .sidebar-section {
        background: rgba(46,139,87,.06); border-radius: 12px;
        padding: 1rem; margin-bottom: 1rem;
    }
    .sidebar-section h4 { margin: 0 0 .75rem 0; color: #2d6a4f; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

st.title(T("title"))
st.markdown(T("subtitle"))
st.subheader(T("soil_header"))

simple_mode = T("simple") in input_mode

if simple_mode:
    col1, col2 = st.columns(2)
    with col1:
        soil_type = st.selectbox(T("soil_type"), list(soil_properties.keys()))
        st.caption(f"pH ≈ {soil_properties[soil_type]['ph']} · "
                   f"N={soil_properties[soil_type]['N']} · "
                   f"P={soil_properties[soil_type]['P']} · "
                   f"K={soil_properties[soil_type]['K']}")
    with col2:
        season = st.selectbox(T("season"), list(season_rainfall.keys()))
        st.caption(f"Expected rainfall ≈ {season_rainfall[season]} mm")

    N        = soil_properties[soil_type]["N"]
    P        = soil_properties[soil_type]["P"]
    K        = soil_properties[soil_type]["K"]
    ph       = soil_properties[soil_type]["ph"]
    rainfall = season_rainfall[season]
else:
    st.info("Enter your soil lab test results. Weather data is fetched automatically.")
    c1, c2, c3 = st.columns(3)
    with c1:
        N  = st.number_input(T("nitrogen"),  0, 150, 50)
        ph = st.slider(T("soil_ph"), 3.0, 9.0, 6.5, 0.1)
    with c2:
        P        = st.number_input(T("phosphorus"), 0, 150, 50)
        rainfall = st.number_input(T("rainfall_mm"), 0.0, 500.0, 200.0)
    with c3:
        K = st.number_input(T("potassium"), 0, 150, 50)

    npk_sum = N + P + K
    if npk_sum > 0:
        if N / npk_sum > 0.6:
            st.markdown('<div class="alert-banner">⚠️ Nitrogen is very high — may favour leafy crops over fruiting ones.</div>', unsafe_allow_html=True)
        if ph < 4.5:
            st.markdown('<div class="alert-banner">⚠️ Highly acidic soil (pH < 4.5). Consider liming.</div>', unsafe_allow_html=True)
        elif ph > 8.0:
            st.markdown('<div class="alert-banner">⚠️ Alkaline soil (pH > 8). May limit nutrient availability.</div>', unsafe_allow_html=True)

st.markdown("")
predict_btn = st.button(T("predict_btn"), type="primary", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
if predict_btn:
    with st.spinner(T("fetching")):
        try:
            rf_model, label_encoder = load_models()
        except FileNotFoundError:
            st.error(T("model_not_found"))
            st.stop()

        temp, humidity, status = get_live_weather(district)
        if temp is None:
            st.error(f"{T('weather_error')}: {status}")
            st.stop()

        features      = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        probabilities = rf_model.predict_proba(features)[0]
        top_n_indices = np.argsort(probabilities)[::-1][:top_n]
        top_n_probs   = probabilities[top_n_indices]
        top_n_crops   = label_encoder.inverse_transform(top_n_indices)

    st.success(T("analysis_done"))
    st.divider()

    # ── Top Recommendation ────────────────────────────────────────────────────
    best_crop  = top_n_crops[0]
    best_label = get_display_name(best_crop)
    best_conf  = top_n_probs[0] * 100
    crop_info  = get_crop_info(best_crop)
    image_data, is_real = fetch_crop_image(best_crop)

    st.markdown(f"""
    <div class="crop-card">
        <p style="font-size:.85rem;opacity:.7;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.25rem">
            {T('top_rec')} · {best_conf:.1f}% AI Confidence
        </p>
        <h2>{crop_info['icon']} {best_label}</h2>
        <p>{T('best_fit')} {district}, {T('best_fit2')}</p>
    </div>
    """, unsafe_allow_html=True)

    img_col, info_col = st.columns([1, 2])
    with img_col:
        caption = T("real_photo") if is_real else f"{crop_info['icon']} {best_label}"
        st.image(image_data, use_container_width=True, caption=caption)

    with info_col:
        st.markdown(
            f'<span class="metric-pill">📅 {crop_info["season"]}</span>&nbsp;'
            f'<span class="metric-pill">💧 {T("water_need")}: {crop_info["water"]}</span>&nbsp;'
            f'<span class="metric-pill">🌡️ {temp}°C · {humidity}%</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown(f"**{T('why_crop')}**")
        st.markdown(
            f"{T('ai_matched')} **{best_label}** {T('based_on')} {ph}, "
            f"N={N}/P={P}/K={K}), {T('live_weather')} {district} "
            f"({temp}°C, {humidity}%), {rainfall} {T('exp_rainfall')} "
            f"{T('hist_align')}"
        )
        st.progress(float(top_n_probs[0]), text=f"{T('confidence')}: **{best_conf:.1f}%**")

        # ── Speak Aloud ──────────────────────────────────────────────────────
        st.markdown("🔊 **Listen to your recommendation**")
        fert_preview = calculate_fertilizer_prescription(best_crop, N, P, K)
        market_preview = get_market_forecast(best_crop)
        tts_text = build_tts_summary(best_label, fert_preview, market_preview, lang=st.session_state.get("lang", "en"))
        render_tts_player(tts_text, lang=st.session_state.get("lang", "en"))

    st.divider()

    # ── Runner-Up Recommendations ─────────────────────────────────────────────
    st.subheader(f"🌱 {T('top_n_recs')}")
    rec_cols = st.columns(min(top_n, 4))
    for i, col in enumerate(rec_cols[:top_n]):
        with col:
            name     = get_display_name(top_n_crops[i])
            conf_pct = top_n_probs[i] * 100
            cinfo    = get_crop_info(top_n_crops[i])
            rank     = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣"][i]
            st.metric(label=f"{rank} {name}", value=f"{conf_pct:.1f}%",
                      delta=f"{cinfo['icon']} {cinfo['season']}")
            st.progress(float(top_n_probs[i]))

    st.divider()

    # ── Environmental Dashboard ───────────────────────────────────────────────
    if show_dashboard:
        st.subheader(T("env_analysis"))
        d1, d2, d3, d4 = st.columns(4)

        def gauge(val, title, rng, color, steps):
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=val,
                title={"text": title, "font": {"size": 14}},
                gauge={"axis": {"range": rng}, "bar": {"color": color}, "steps": steps},
            ))
            fig.update_layout(height=220, margin=dict(l=10,r=10,t=30,b=10))
            return fig

        with d1:
            st.plotly_chart(gauge(temp, "Temperature °C", [0,50], "#e05252",
                [{"range":[0,20],"color":"#cce5ff"},{"range":[20,35],"color":"#d4edda"},{"range":[35,50],"color":"#f8d7da"}]),
                use_container_width=True)
        with d2:
            st.plotly_chart(gauge(humidity, "Humidity %", [0,100], "#4a90d9",
                [{"range":[0,40],"color":"#e2e3e5"},{"range":[40,70],"color":"#d4edda"},{"range":[70,100],"color":"#cce5ff"}]),
                use_container_width=True)
        with d3:
            ph_col = "#52b788" if 5.5 <= ph <= 7.5 else "#e76f51"
            st.plotly_chart(gauge(ph, "Soil pH", [3,9], ph_col,
                [{"range":[3,5.5],"color":"#f8d7da"},{"range":[5.5,7.5],"color":"#d4edda"},{"range":[7.5,9],"color":"#fff3cd"}]),
                use_container_width=True)
        with d4:
            st.plotly_chart(gauge(rainfall, "Rainfall mm", [0,500], "#4895ef",
                [{"range":[0,100],"color":"#fff3cd"},{"range":[100,250],"color":"#d4edda"},{"range":[250,500],"color":"#cce5ff"}]),
                use_container_width=True)

        radar_col, bar_col = st.columns(2)
        with radar_col:
            fig_npk = go.Figure(go.Scatterpolar(
                r=[N,P,K,N], theta=["Nitrogen (N)","Phosphorus (P)","Potassium (K)","Nitrogen (N)"],
                fill="toself", line_color="#2d6a4f", fillcolor="rgba(45,106,79,0.25)",
            ))
            fig_npk.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max(150,N,P,K)+10])),
                showlegend=False, title={"text":"Soil NPK Balance","x":0.5},
                height=300, margin=dict(l=30,r=30,t=50,b=30),
            )
            st.plotly_chart(fig_npk, use_container_width=True)

        with bar_col:
            crop_labels = [get_display_name(c) for c in top_n_crops]
            conf_pcts   = [p*100 for p in top_n_probs]
            colors      = ["#2d6a4f" if i==0 else "#74c69d" for i in range(len(crop_labels))]
            fig_bar = go.Figure(go.Bar(
                x=conf_pcts, y=crop_labels, orientation="h",
                marker_color=colors, text=[f"{c:.1f}%" for c in conf_pcts], textposition="outside",
            ))
            fig_bar.update_layout(
                title={"text":"AI Confidence Scores","x":0.5},
                xaxis=dict(range=[0,105], title="Confidence %"),
                yaxis=dict(autorange="reversed"),
                height=300, margin=dict(l=10,r=40,t=50,b=40),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        st.divider()

    # ── UPGRADE 6B: Fertilizer Prescription ──────────────────────────────────
    st.subheader(T("fert_title"))
    st.markdown(T("fert_desc"))

    fert = calculate_fertilizer_prescription(best_crop, N, P, K)

    if fert["all_optimal"]:
        st.success(T("fert_optimal"))
    else:
        req = fert["required"]
        f1, f2, f3 = st.columns(3)

        with f1:
            deficit = fert["deficit_N"]
            status_n = "normal" if deficit == 0 else "inverse"
            st.metric(label=f"🟡 {T('nitrogen')}", value=f"{N} kg/ha",
                      delta=f"Need {req['N']} | Deficit: {deficit}", delta_color=status_n)
        with f2:
            deficit = fert["deficit_P"]
            status_p = "normal" if deficit == 0 else "inverse"
            st.metric(label=f"🟠 {T('phosphorus')}", value=f"{P} kg/ha",
                      delta=f"Need {req['P']} | Deficit: {deficit}", delta_color=status_p)
        with f3:
            deficit = fert["deficit_K"]
            status_k = "normal" if deficit == 0 else "inverse"
            st.metric(label=f"🔵 {T('potassium')}", value=f"{K} kg/ha",
                      delta=f"Need {req['K']} | Deficit: {deficit}", delta_color=status_k)

        st.markdown('<div class="fert-card">', unsafe_allow_html=True)
        st.markdown("**Prescription (per hectare):**")
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            if fert["urea_kg"] > 0:
                st.metric("🟡 Urea (46% N)", f"{fert['urea_kg']} kg", T("kg_per_ha"))
            else:
                st.metric("🟡 Urea", T("no_deficit"))
        with pc2:
            if fert["dap_kg"] > 0:
                st.metric("🟠 DAP (18N+46P)", f"{fert['dap_kg']} kg", T("kg_per_ha"))
            else:
                st.metric("🟠 DAP", T("no_deficit"))
        with pc3:
            if fert["mop_kg"] > 0:
                st.metric("🔵 MOP (60% K)", f"{fert['mop_kg']} kg", T("kg_per_ha"))
            else:
                st.metric("🔵 MOP", T("no_deficit"))
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ── UPGRADE 6C: Market & Economics Forecaster ─────────────────────────────
    st.subheader(T("market_title"))
    market = get_market_forecast(best_crop)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(T("market_price"),   f"₹{market['price_per_q']:,}", "/quintal")
    m2.metric(T("market_yield"),   f"{market['yield_q_ha']} q",   T("per_ha"))
    m3.metric(T("market_revenue"), f"₹{market['revenue']:,}",     T("per_ha"))
    m4.metric(T("market_cost"),    f"₹{market['input_cost']:,}",  T("per_ha"))
    profit_color = "normal" if market["net_profit"] > 0 else "inverse"
    m5.metric(T("market_profit"),  f"₹{market['net_profit']:,}",
              f"ROI: {market['roi_pct']}%", delta_color=profit_color)

    st.markdown('<div class="market-card">', unsafe_allow_html=True)

    # Profit waterfall chart
    fig_waterfall = go.Figure(go.Waterfall(
        name="Economics",
        orientation="v",
        measure=["relative", "relative", "total"],
        x=[T("market_revenue"), f"- {T('market_cost')}", T("market_profit")],
        y=[market["revenue"], -market["input_cost"], 0],
        connector={"line": {"color": "rgba(63,63,63,.4)"}},
        increasing={"marker": {"color": "#2d6a4f"}},
        decreasing={"marker": {"color": "#e05252"}},
        totals={"marker": {"color": "#4895ef"}},
        text=[f"₹{market['revenue']:,}", f"-₹{market['input_cost']:,}", f"₹{market['net_profit']:,}"],
        textposition="outside",
    ))
    fig_waterfall.update_layout(
        title={"text": f"Economics per Hectare — {best_label}", "x": 0.5},
        yaxis_title="INR (₹)", height=320,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)
    st.caption(f"ℹ️ {T('market_note')}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ── Optional: History Table ───────────────────────────────────────────────
    if show_history:
        st.subheader(T("history_title"))
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({
            T("district_lbl"): district,
            "Temp (°C)": temp, "Humidity %": humidity,
            "pH": ph, "Rainfall mm": rainfall,
            "Top Pick": best_label, "Confidence": f"{best_conf:.1f}%",
        })
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)
        if st.button(T("clear_history")):
            st.session_state.history = []
            st.rerun()

    # ── PDF Export ────────────────────────────────────────────────────────────
    st.write(f"### {T('export_title')}")
    st.write(T("export_desc"))

    pdf_bytes = create_pdf_report(
        district, best_label, best_conf,
        temp, humidity, ph, rainfall, N, P, K,
        fert, market,
        lang=st.session_state.get("lang", "en"),
    )
    st.download_button(
        label=T("download_pdf"),
        data=pdf_bytes,
        file_name=f"{district}_Crop_Report_{datetime.date.today()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.divider()

    # ── Input Summary ─────────────────────────────────────────────────────────
    with st.expander(T("input_summary")):
        summary = {
            T("district_lbl"):  district,
            T("temperature"):   temp,
            T("humidity"):      humidity,
            T("nitrogen"):      N,
            T("phosphorus"):    P,
            T("potassium"):     K,
            T("soil_ph"):       ph,
            T("rainfall_mm"):   rainfall,
        }
        st.table(pd.DataFrame.from_dict(summary, orient="index", columns=[T("value")]))