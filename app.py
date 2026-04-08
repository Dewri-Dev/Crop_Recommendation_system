"""
Assam Crop Recommendation System
Upgraded: Better UI/UX, new features, improved code architecture
49 Assam-specific crops supported.
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

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .crop-card {
        background: linear-gradient(135deg, #1a472a 0%, #2d6a4f 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        color: white;
        margin: 1rem 0;
    }
    .crop-card h2 { margin: 0 0 .25rem 0; font-size: 2rem; }
    .crop-card p  { margin: 0; opacity: .85; font-size: .95rem; }
    .metric-pill {
        display: inline-flex; align-items: center; gap: .4rem;
        background: rgba(46, 139, 87, .12);
        border: 1px solid rgba(46, 139, 87, .25);
        border-radius: 999px;
        padding: .35rem .9rem;
        font-size: .85rem;
        font-weight: 500;
    }
    .conf-row { margin: .5rem 0; }
    .conf-label {
        font-size: .9rem;
        font-weight: 500;
        margin-bottom: .25rem;
        display: flex;
        justify-content: space-between;
    }
    .alert-banner {
        border-left: 4px solid #f0a500;
        background: rgba(240, 165, 0, .08);
        border-radius: 0 8px 8px 0;
        padding: .75rem 1rem;
        font-size: .9rem;
    }
    .sidebar-section {
        background: rgba(46, 139, 87, .06);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .sidebar-section h4 { margin: 0 0 .75rem 0; color: #2d6a4f; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── PDF Report Generator ─────────────────────────────────────────────────────

def create_pdf_report(district, crop_name, confidence, temp, humidity, ph, rainfall, N, P, K):
    """Generates a professional PDF report from the AI prediction."""
    pdf = FPDF()
    pdf.add_page()

    # 1. Header
    pdf.set_font("Helvetica", 'B', 20)
    pdf.set_text_color(46, 139, 87)
    pdf.cell(0, 15, "AI Crop Recommendation Report", ln=True, align='C')

    pdf.ln(5)

    # 2. General Info
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Date Generated: {datetime.date.today().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(0, 10, f"Analyzed Location: {district.title()}, Assam", ln=True)

    pdf.ln(5)

    # 3. The AI Prediction
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, f"Top Recommended Crop: {crop_name} ({confidence:.1f}% AI Confidence)", ln=True)

    pdf.ln(5)

    # 4. The Environmental Data Used
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Environmental & Soil Data Analyzed:", ln=True)

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"- Live Temperature: {temp} C", ln=True)
    pdf.cell(0, 10, f"- Live Humidity: {humidity} %", ln=True)
    pdf.cell(0, 10, f"- Expected Rainfall: {rainfall} mm", ln=True)
    pdf.cell(0, 10, f"- Estimated Soil pH: {ph}", ln=True)
    pdf.cell(0, 10, f"- Nitrogen (N): {N} | Phosphorus (P): {P} | Potassium (K): {K}", ln=True)

    pdf.ln(15)

    # 5. Footer
    pdf.set_font("Helvetica", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "This report was generated automatically by the Assam Crop Recommendation System.", align='C')

    return bytes(pdf.output())


# ─── Image Fetching (Fixed for 49 crops) ─────────────────────────────────────

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
    "rice":          "Rice",
    "wheat":         "Wheat",
    "maize":         "Maize",
    "jute":          "Jute",
    "assam_tea":     "Assam_tea",
    "coffee":        "Coffea",
    "mustard":       "Mustard_plant",
    "sugarcane":     "Sugarcane",
    "cotton":        "Cotton",
    "banana":        "Banana",
    "mango":         "Mango",
    "chickpea":      "Chickpea",
    "lentil":        "Lentil",
    "papaya":        "Papaya",
    "coconut":       "Coconut",
    "pomegranate":   "Pomegranate",
    "grapes":        "Grape",
    "watermelon":    "Watermelon",
    "muskmelon":     "Muskmelon",
    "orange":        "Orange_(fruit)",
    "apple":         "Apple",
    "mungbean":      "Mung_bean",
    "mothbeans":     "Moth_bean",
    "pigeonpeas":    "Pigeon_pea",
    "kidneybeans":   "Kidney_bean",
    "blackgram":     "Vigna_mungo",
    "joha_rice":     "Joha_rice",
    "joha_rice72":   "Joha_rice",
    "bao_rice":      "Bao_rice",
    "bora_rice":     "Glutinous_rice",
    "chokuwa_rice":  "Chokuwa_rice",
    "komal_saul":    "Komal_saul",
    "xaaj_rice":     "Xaj_(drink)",
    "apong_rice":    "Apong",
    "bhut_jolokia":  "Bhut_jolokia",
    "kaji_nemu":     "Kaji_Nemu",
    "ou_tenga":      "Elephant_apple",
    "thekera":       "Garcinia_pedunculata",
    "amlokhi":       "Phyllanthus_emblica",
    "bogori":        "Ziziphus_mauritiana",
    "leteku":        "Baccaurea_ramiflora",
    "jalpai":        "Elaeocarpus_floribundus",
    "areca_nut":     "Areca_nut",
    "betel_leaf":    "Betel",
    "kola_banana":   "Banana",
    "lai_xaak":      "Brassica_juncea",
    "kosu":          "Colocasia_esculenta",
    "dhekia_xaak":   "Diplazium_esculentum",
    "manimuni":      "Centella_asiatica",
    "local_brinjal": "Brinjal",
    "local_pumpkin": "Pumpkin",
    "local_beans":   "Bean",
    "bamboo_shoot":  "Bamboo_shoot",
}

_CROP_DISPLAY_NAMES = {
    "joha_rice":     "Joha Rice",
    "joha_rice72":   "Joha Rice (72)",
    "bao_rice":      "Bao Rice",
    "bora_rice":     "Bora Rice (Glutinous)",
    "chokuwa_rice":  "Chokuwa Rice",
    "komal_saul":    "Komal Saul (Soft Rice)",
    "xaaj_rice":     "Xaaj Rice",
    "apong_rice":    "Apong Rice",
    "bhut_jolokia":  "Bhut Jolokia (Ghost Pepper)",
    "kaji_nemu":     "Kaji Nemu (Assam Lemon)",
    "ou_tenga":      "Ou Tenga (Elephant Apple)",
    "thekera":       "Thekera",
    "amlokhi":       "Amlokhi (Indian Gooseberry)",
    "bogori":        "Bogori (Indian Jujube)",
    "leteku":        "Leteku",
    "jalpai":        "Jalpai (Indian Olive)",
    "areca_nut":     "Areca Nut (Tamul)",
    "betel_leaf":    "Betel Leaf (Pan)",
    "kola_banana":   "Kola Banana",
    "lai_xaak":      "Lai Xaak (Mustard Greens)",
    "kosu":          "Kosu (Taro)",
    "dhekia_xaak":   "Dhekia Xaak (Edible Fern)",
    "manimuni":      "Manimuni (Pennywort)",
    "local_brinjal": "Local Brinjal",
    "local_pumpkin": "Local Pumpkin",
    "local_beans":   "Local Beans",
    "bamboo_shoot":  "Bamboo Shoot",
    "assam_tea":     "Assam Tea",
}


def get_display_name(crop_key: str) -> str:
    if crop_key in _CROP_DISPLAY_NAMES:
        return _CROP_DISPLAY_NAMES[crop_key]
    return crop_key.replace("_", " ").title()


def _get_image_bytes(url: str) -> bytes | None:
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
    if not any(url_lower.endswith(ext) or (ext + "?") in url_lower
               for ext in _VALID_EXTS):
        return False
    if any(kw in url_lower for kw in _SKIP_KEYWORDS):
        return False
    return True


def _try_wikipedia_infobox(crop_key: str) -> bytes | None:
    title = _CROP_WIKI_TITLES.get(crop_key.lower())
    if not title:
        return None
    try:
        api = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&titles={title}&prop=pageimages"
            "&pithumbsize=600&format=json&origin=*"
        )
        r = requests.get(api, headers={"User-Agent": "AssamCropRecommender/2.0"},
                         timeout=10, verify=False)
        if r.status_code != 200:
            return None
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


def _try_wikimedia_search(crop_name: str) -> bytes | None:
    query = urllib.parse.quote(f"{crop_name} crop plant field")
    try:
        api = (
            "https://commons.wikimedia.org/w/api.php"
            f"?action=query&generator=search&gsrnamespace=6&gsrsearch={query}"
            "&prop=imageinfo&iiprop=url&iiurlwidth=600"
            "&format=json&origin=*&gsrlimit=25"
        )
        r = requests.get(api, headers={"User-Agent": "AssamCropRecommender/2.0"},
                         timeout=10, verify=False)
        if r.status_code != 200:
            return None
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
        r = int(26  + (45  - 26)  * t)
        g = int(71  + (106 - 71)  * t)
        b = int(42  + (79  - 42)  * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    label    = crop_name.replace("_", " ").title()
    initials = "".join(w[0].upper() for w in label.split()[:2])
    try:
        font_big  = ImageFont.truetype("arial.ttf", 80)
        font_main = ImageFont.truetype("arial.ttf", 52)
        font_sub  = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font_big = font_main = font_sub = ImageFont.load_default()
    draw.text((W // 2, H // 2 - 80), initials,  font=font_big,  fill=(255, 255, 255, 30), anchor="mm")
    draw.text((W // 2, H // 2 + 20), label,     font=font_main, fill=(255, 255, 255),     anchor="mm")
    draw.text((W // 2, H // 2 + 90), "No photo available", font=font_sub, fill=(180, 220, 180), anchor="mm")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@st.cache_data(ttl=86_400, show_spinner=False)
def fetch_crop_image(crop_name: str) -> tuple[bytes, bool]:
    crop_key = crop_name.lower().replace(" ", "_")
    img = _try_wikipedia_infobox(crop_key)
    if img:
        return img, True
    img = _try_wikimedia_search(crop_name)
    if img:
        return img, True
    return _make_placeholder_png(crop_name), False


# ─── Data & Model Loading ─────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_models():
    model   = pickle.load(open("model/crop_model.pkl",    "rb"))
    encoder = pickle.load(open("model/label_encoder.pkl", "rb"))
    return model, encoder


# ─── Crop Info for all 49 crops ───────────────────────────────────────────────
CROP_INFO: dict[str, dict] = {
    "rice":          {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "wheat":         {"season": "Rabi (Nov-Apr)",      "water": "Medium", "icon": "🌿"},
    "maize":         {"season": "Kharif / Rabi",       "water": "Medium", "icon": "🌽"},
    "jute":          {"season": "Kharif (Mar-Jul)",    "water": "High",   "icon": "🌱"},
    "assam_tea":     {"season": "Year-round",          "water": "High",   "icon": "🍵"},
    "mustard":       {"season": "Rabi (Oct-Mar)",      "water": "Low",    "icon": "🌼"},
    "sugarcane":     {"season": "Year-round",          "water": "High",   "icon": "🎋"},
    "cotton":        {"season": "Kharif (Apr-Nov)",    "water": "Medium", "icon": "☁️"},
    "banana":        {"season": "Year-round",          "water": "Medium", "icon": "🍌"},
    "mango":         {"season": "Summer (Mar-Jun)",    "water": "Low",    "icon": "🥭"},
    "chickpea":      {"season": "Rabi (Oct-Mar)",      "water": "Low",    "icon": "🫘"},
    "lentil":        {"season": "Rabi (Oct-Mar)",      "water": "Low",    "icon": "🫘"},
    "papaya":        {"season": "Year-round",          "water": "Medium", "icon": "🍈"},
    "coconut":       {"season": "Year-round",          "water": "High",   "icon": "🥥"},
    "pomegranate":   {"season": "Summer / Winter",     "water": "Low",    "icon": "🍎"},
    "grapes":        {"season": "Winter (Oct-Feb)",    "water": "Medium", "icon": "🍇"},
    "watermelon":    {"season": "Summer (Mar-Jun)",    "water": "Low",    "icon": "🍉"},
    "muskmelon":     {"season": "Summer (Feb-May)",    "water": "Low",    "icon": "🍈"},
    "orange":        {"season": "Winter (Dec-Feb)",    "water": "Medium", "icon": "🍊"},
    "apple":         {"season": "Summer (Jun-Sep)",    "water": "Medium", "icon": "🍎"},
    "mungbean":      {"season": "Kharif / Summer",     "water": "Low",    "icon": "🫘"},
    "mothbeans":     {"season": "Kharif (Jun-Sep)",    "water": "Low",    "icon": "🫘"},
    "pigeonpeas":    {"season": "Kharif (Jun-Nov)",    "water": "Low",    "icon": "🫘"},
    "kidneybeans":   {"season": "Kharif (Jun-Sep)",    "water": "Medium", "icon": "🫘"},
    "blackgram":     {"season": "Kharif / Rabi",       "water": "Low",    "icon": "🫘"},
    "coffee":        {"season": "Year-round",          "water": "Medium", "icon": "☕"},
    "joha_rice":     {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "joha_rice72":   {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "bao_rice":      {"season": "Kharif (Jun-Dec)",   "water": "High",   "icon": "🌾"},
    "bora_rice":     {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "chokuwa_rice":  {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "komal_saul":    {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "xaaj_rice":     {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "apong_rice":    {"season": "Kharif (Jun-Nov)",   "water": "High",   "icon": "🌾"},
    "bhut_jolokia":  {"season": "Kharif (Jul-Oct)",   "water": "Medium", "icon": "🌶️"},
    "kaji_nemu":     {"season": "Year-round",          "water": "Medium", "icon": "🍋"},
    "ou_tenga":      {"season": "Monsoon (Jun-Sep)",  "water": "Medium", "icon": "🍏"},
    "thekera":       {"season": "Monsoon (Jun-Sep)",  "water": "Medium", "icon": "🍋"},
    "amlokhi":       {"season": "Rabi (Oct-Feb)",     "water": "Low",    "icon": "🟢"},
    "bogori":        {"season": "Winter (Oct-Jan)",   "water": "Low",    "icon": "🫐"},
    "leteku":        {"season": "Summer (Apr-Jun)",   "water": "Medium", "icon": "🍇"},
    "jalpai":        {"season": "Monsoon (Jul-Sep)",  "water": "Medium", "icon": "🫒"},
    "areca_nut":     {"season": "Year-round",          "water": "High",   "icon": "🌴"},
    "betel_leaf":    {"season": "Year-round",          "water": "High",   "icon": "🍃"},
    "kola_banana":   {"season": "Year-round",          "water": "Medium", "icon": "🍌"},
    "lai_xaak":      {"season": "Rabi (Oct-Feb)",     "water": "Medium", "icon": "🥬"},
    "kosu":          {"season": "Year-round",          "water": "High",   "icon": "🌿"},
    "dhekia_xaak":   {"season": "Monsoon (Jun-Sep)",  "water": "High",   "icon": "🌿"},
    "manimuni":      {"season": "Year-round",          "water": "Medium", "icon": "🌿"},
    "local_brinjal": {"season": "Year-round",          "water": "Medium", "icon": "🍆"},
    "local_pumpkin": {"season": "Kharif (Jun-Oct)",   "water": "Medium", "icon": "🎃"},
    "local_beans":   {"season": "Kharif / Rabi",       "water": "Medium", "icon": "🫘"},
    "bamboo_shoot":  {"season": "Monsoon (Jun-Aug)",  "water": "High",   "icon": "🎍"},
}


def get_crop_info(crop_key: str) -> dict:
    return CROP_INFO.get(crop_key.lower(), {"season": "—", "water": "—", "icon": "🌱"})


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://placehold.co/300x80/1a472a/white?text=Assam+Crop+Advisor",
             use_container_width=True)
    st.markdown("---")

    st.markdown('<div class="sidebar-section"><h4>📍 Location</h4>', unsafe_allow_html=True)
    district = st.text_input(
        "District / City",
        value="Guwahati",
        help="Used to fetch live temperature & humidity",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h4>⚙️ Input Mode</h4>', unsafe_allow_html=True)
    input_mode = st.radio(
        "Choose mode",
        ["👨‍🌾 Simple Mode", "🔬 Advanced Mode"],
        help="Simple: pick soil type. Advanced: enter exact lab values.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h4>📊 Display Options</h4>', unsafe_allow_html=True)
    show_dashboard = st.toggle("Show environmental dashboard", value=True)
    show_history   = st.toggle("Show crop history comparison",  value=False)
    top_n          = st.slider("Number of recommendations", 3, 7, 3)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Built for Assam farmers · v2.0\nPowered by Random Forest ML")


# ─── Main Content ─────────────────────────────────────────────────────────────
st.title("🌾 Assam Crop Recommendation System")
st.markdown("*AI-powered crop advice tailored to your soil, weather, and location.*")

# ─── Input Section ────────────────────────────────────────────────────────────
st.subheader("🌱 Soil & Season Details")

if "Simple" in input_mode:
    col1, col2 = st.columns(2)
    with col1:
        soil_type = st.selectbox("Soil Type", list(soil_properties.keys()))
        st.caption(f"pH ≈ {soil_properties[soil_type]['ph']} · "
                   f"N={soil_properties[soil_type]['N']} · "
                   f"P={soil_properties[soil_type]['P']} · "
                   f"K={soil_properties[soil_type]['K']}")
    with col2:
        season = st.selectbox("Current Season", list(season_rainfall.keys()))
        st.caption(f"Expected rainfall ≈ {season_rainfall[season]} mm")

    N        = soil_properties[soil_type]["N"]
    P        = soil_properties[soil_type]["P"]
    K        = soil_properties[soil_type]["K"]
    ph       = soil_properties[soil_type]["ph"]
    rainfall = season_rainfall[season]

else:
    st.info("Enter your soil lab test results. Weather data is still fetched automatically.")
    c1, c2, c3 = st.columns(3)
    with c1:
        N  = st.number_input("Nitrogen (N)",    0, 150, 50)
        ph = st.slider("Soil pH",   3.0, 9.0, 6.5, 0.1)
    with c2:
        P        = st.number_input("Phosphorus (P)", 0, 150, 50)
        rainfall = st.number_input("Rainfall (mm)",  0.0, 500.0, 200.0)
    with c3:
        K = st.number_input("Potassium (K)", 0, 150, 50)

    npk_sum = N + P + K
    if npk_sum > 0:
        pct_n = N / npk_sum
        if pct_n > 0.6:
            st.markdown('<div class="alert-banner">⚠️ Nitrogen is very high — may favour leafy crops over fruiting ones.</div>', unsafe_allow_html=True)
        if ph < 4.5:
            st.markdown('<div class="alert-banner">⚠️ Soil is highly acidic (pH < 4.5). Consider liming before planting.</div>', unsafe_allow_html=True)
        elif ph > 8.0:
            st.markdown('<div class="alert-banner">⚠️ Soil is alkaline (pH > 8). May limit nutrient availability.</div>', unsafe_allow_html=True)

st.markdown("")

# ─── Predict ─────────────────────────────────────────────────────────────────
predict_btn = st.button("🚀 Get Crop Recommendations", type="primary", use_container_width=True)

if predict_btn:
    with st.spinner("Fetching live weather data and running AI analysis…"):
        try:
            rf_model, label_encoder = load_models()
        except FileNotFoundError:
            st.error("⚠️ Model files not found! Run `train_model.ipynb` first.")
            st.stop()

        temp, humidity, status = get_live_weather(district)

        if temp is None:
            st.error(f"Weather API Error: {status}")
            st.stop()

        features      = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        probabilities = rf_model.predict_proba(features)[0]

        top_n_indices = np.argsort(probabilities)[::-1][:top_n]
        top_n_probs   = probabilities[top_n_indices]
        top_n_crops   = label_encoder.inverse_transform(top_n_indices)

        st.success("✅ Analysis complete!")
        st.divider()

        # ── Top Recommendation ────────────────────────────────────────────────
        best_crop   = top_n_crops[0]
        best_label  = get_display_name(best_crop)
        best_conf   = top_n_probs[0] * 100
        crop_info   = get_crop_info(best_crop)

        image_data, is_real = fetch_crop_image(best_crop)

        st.markdown(f"""
        <div class="crop-card">
            <p style="font-size:.85rem;opacity:.7;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.25rem">
                Top Recommendation · {best_conf:.1f}% AI Confidence
            </p>
            <h2>{crop_info['icon']} {best_label}</h2>
            <p>Best fit for your soil composition, current weather in {district}, and seasonal conditions.</p>
        </div>
        """, unsafe_allow_html=True)

        img_col, info_col = st.columns([1, 2])

        with img_col:
            caption = "📸 Real photo" if is_real else f"{crop_info['icon']} {best_label}"
            st.image(image_data, use_container_width=True, caption=caption)

        with info_col:
            st.markdown(
                f'<span class="metric-pill">📅 {crop_info["season"]}</span>&nbsp;'
                f'<span class="metric-pill">💧 Water need: {crop_info["water"]}</span>&nbsp;'
                f'<span class="metric-pill">🌡️ {temp}°C · {humidity}% humidity</span>',
                unsafe_allow_html=True,
            )
            st.markdown("")
            st.markdown("**Why this crop?**")
            st.markdown(
                f"The AI matched **{best_label}** based on your soil (pH {ph}, "
                f"N={N}/P={P}/K={K}), live weather in {district} "
                f"({temp}°C, {humidity}% humidity), and {rainfall} mm expected rainfall. "
                f"These conditions closely align with historical growing data for this crop in Assam."
            )
            st.progress(float(top_n_probs[0]),
                        text=f"Model confidence: **{best_conf:.1f}%**")

        st.divider()

        # ── Runner-Up Recommendations ─────────────────────────────────────────
        st.subheader(f"🌱 Top {top_n} Recommendations")
        rec_cols = st.columns(min(top_n, 4))

        for i, col in enumerate(rec_cols[:top_n]):
            with col:
                name      = get_display_name(top_n_crops[i])
                conf_pct  = top_n_probs[i] * 100
                cinfo     = get_crop_info(top_n_crops[i])
                rank_icon = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣"][i]
                st.metric(
                    label=f"{rank_icon} {name}",
                    value=f"{conf_pct:.1f}%",
                    delta=f"{cinfo['icon']} {cinfo['season']}",
                )
                st.progress(float(top_n_probs[i]))

        st.divider()

        # ── Environmental Dashboard ───────────────────────────────────────────
        if show_dashboard:
            st.subheader("📊 Environmental Analysis")

            dash_c1, dash_c2, dash_c3, dash_c4 = st.columns(4)

            with dash_c1:
                fig_temp = go.Figure(go.Indicator(
                    mode="gauge+number", value=temp,
                    title={"text": "Temperature °C", "font": {"size": 14}},
                    gauge={"axis": {"range": [0, 50]}, "bar": {"color": "#e05252"},
                           "steps": [{"range": [0, 20], "color": "#cce5ff"},
                                     {"range": [20, 35], "color": "#d4edda"},
                                     {"range": [35, 50], "color": "#f8d7da"}]},
                ))
                fig_temp.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_temp, use_container_width=True)

            with dash_c2:
                fig_hum = go.Figure(go.Indicator(
                    mode="gauge+number", value=humidity,
                    title={"text": "Humidity %", "font": {"size": 14}},
                    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#4a90d9"},
                           "steps": [{"range": [0, 40], "color": "#e2e3e5"},
                                     {"range": [40, 70], "color": "#d4edda"},
                                     {"range": [70, 100], "color": "#cce5ff"}]},
                ))
                fig_hum.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_hum, use_container_width=True)

            with dash_c3:
                ph_color = "#52b788" if 5.5 <= ph <= 7.5 else "#e76f51"
                fig_ph = go.Figure(go.Indicator(
                    mode="gauge+number", value=ph,
                    title={"text": "Soil pH", "font": {"size": 14}},
                    gauge={"axis": {"range": [3, 9]}, "bar": {"color": ph_color},
                           "steps": [{"range": [3.0, 5.5], "color": "#f8d7da"},
                                     {"range": [5.5, 7.5], "color": "#d4edda"},
                                     {"range": [7.5, 9.0], "color": "#fff3cd"}]},
                ))
                fig_ph.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_ph, use_container_width=True)

            with dash_c4:
                fig_rain = go.Figure(go.Indicator(
                    mode="gauge+number", value=rainfall,
                    title={"text": "Rainfall mm", "font": {"size": 14}},
                    gauge={"axis": {"range": [0, 500]}, "bar": {"color": "#4895ef"},
                           "steps": [{"range": [0, 100], "color": "#fff3cd"},
                                     {"range": [100, 250], "color": "#d4edda"},
                                     {"range": [250, 500], "color": "#cce5ff"}]},
                ))
                fig_rain.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_rain, use_container_width=True)

            radar_col, bar_col = st.columns(2)

            with radar_col:
                fig_npk = go.Figure(go.Scatterpolar(
                    r=[N, P, K, N],
                    theta=["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "Nitrogen (N)"],
                    fill="toself",
                    line_color="#2d6a4f",
                    fillcolor="rgba(45,106,79,0.25)",
                ))
                fig_npk.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, max(150, N, P, K) + 10])),
                    showlegend=False,
                    title={"text": "Soil NPK Balance", "x": 0.5},
                    height=300, margin=dict(l=30, r=30, t=50, b=30),
                )
                st.plotly_chart(fig_npk, use_container_width=True)

            with bar_col:
                crop_labels = [get_display_name(c) for c in top_n_crops]
                conf_pcts   = [p * 100 for p in top_n_probs]
                colors      = ["#2d6a4f" if i == 0 else "#74c69d" for i in range(len(crop_labels))]
                fig_bar = go.Figure(go.Bar(
                    x=conf_pcts, y=crop_labels, orientation="h",
                    marker_color=colors,
                    text=[f"{c:.1f}%" for c in conf_pcts],
                    textposition="outside",
                ))
                fig_bar.update_layout(
                    title={"text": "AI Confidence Scores", "x": 0.5},
                    xaxis=dict(range=[0, 105], title="Confidence %"),
                    yaxis=dict(autorange="reversed"),
                    height=300, margin=dict(l=10, r=40, t=50, b=40),
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            st.divider()

        # ── Optional: Comparison History Table ───────────────────────────────
        if show_history:
            st.subheader("📋 Recommendation History (This Session)")
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "District":    district,
                "Temp (°C)":   temp,
                "Humidity %":  humidity,
                "pH":          ph,
                "Rainfall mm": rainfall,
                "Top Pick":    best_label,
                "Confidence":  f"{best_conf:.1f}%",
            })
            df_history = pd.DataFrame(st.session_state.history)
            st.dataframe(df_history, use_container_width=True, hide_index=True)
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.rerun()

        # ── PDF Report Export ─────────────────────────────────────────────────
        st.write("### 🖨️ Export Results")
        st.write("Download a printable summary of this analysis for field use.")

        pdf_bytes = create_pdf_report(
            district, best_label, best_conf,
            temp, humidity, ph, rainfall, N, P, K
        )

        st.download_button(
            label="📄 Download Official PDF Report",
            data=pdf_bytes,
            file_name=f"{district}_Crop_Report_{datetime.date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.divider()

        # ── Input Summary ─────────────────────────────────────────────────────
        with st.expander("🔍 View full input summary used for this prediction"):
            summary = {
                "District":          district,
                "Temperature (°C)":  temp,
                "Humidity (%)":      humidity,
                "Nitrogen (N)":      N,
                "Phosphorus (P)":    P,
                "Potassium (K)":     K,
                "Soil pH":           ph,
                "Rainfall (mm)":     rainfall,
            }
            st.table(pd.DataFrame.from_dict(summary, orient="index", columns=["Value"]))