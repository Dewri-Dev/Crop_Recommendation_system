import streamlit as st
import streamlit.components.v1 as components
import requests, pickle, numpy as np, plotly.graph_objects as go
import pandas as pd
from PIL import Image
from io import BytesIO
import datetime, urllib3, urllib.parse, base64, json, re, os, io, urllib.request
from dotenv import load_dotenv

# Local Imports
from mappings import soil_properties, season_rainfall
from weather import get_live_weather
from logic.fertilizer import calculate_fertilizer_prescription
from logic.market import get_market_forecast
from logic.pdf_generator import create_pdf_report
from services.local_vision_service import identify_crop_ai
from services.wikipedia_service import fetch_crop_image
from utils.logger import logger
from utils.database import init_db, save_report, get_all_reports, clear_all_reports, get_regional_analytics

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# Initialize Database
init_db()

st.set_page_config(page_title="Assam Crop Advisor", page_icon="🌾",
                   layout="wide", initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_config_data():
    with open("config/translations.json", "r", encoding="utf-8") as f:
        translations = json.load(f)
    with open("config/crop_data.json", "r", encoding="utf-8") as f:
        crop_data = json.load(f)
    return translations, crop_data

UI_TEXT, CROP_DATA = load_config_data()

def T(key):
    lang = st.session_state.get("lang","en")
    return UI_TEXT.get(lang, UI_TEXT["en"]).get(key, key)


# ═══════════════════════════════════════════════════════════════════════════════
# TTS PLAYER & DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def build_tts_summary(crop_name, fert, market, lang="en", crop_key=None):
    if crop_key in CROP_DATA["facts"]:
        fact = CROP_DATA["facts"][crop_key].get(lang, CROP_DATA["facts"][crop_key]["en"])
        if lang == "as":
            return f"{crop_name}ৰ বিষয়ে কিছু তথ্য: {fact}"
        return f"Few facts about {crop_name}: {fact}"

    if lang == "as":
        return (f"শীৰ্ষ পৰামৰ্শিত শস্য: {crop_name}। "
                f"ইউৰিয়া {fert['urea_kg']} কেজি, DAP {fert['dap_kg']} কেজি, "
                f"MOP {fert['mop_kg']} কেজি প্ৰতি হেক্টৰত প্ৰয়োগ কৰক। "
                f"নিট লাভ {market['net_profit']:,} টকা। ROI: {market['roi_pct']} শতাংশ।")
    return (f"Top recommended crop: {crop_name}. "
            f"Apply {fert['urea_kg']} kg Urea, {fert['dap_kg']} kg DAP, "
            f"and {fert['mop_kg']} kg MOP per hectare. "
            f"Estimated net profit: Rupees {market['net_profit']:,}. "
            f"Return on investment: {market['roi_pct']} percent.")

def render_tts_player(text, lang="en"):
    lang_code = "as-IN" if lang == "as" else "en-IN"
    escaped   = text.replace("\\","\\\\").replace("'","\\'").replace('"','\\"').replace("\n"," ")
    preview   = text[:80] + "…" if len(text) > 80 else text
    components.html(f"""
<div style="display:flex;align-items:center;gap:10px;padding:.65rem 1rem;
     background:rgba(37,99,235,.08);border:1px solid rgba(37,99,235,.2);
     border-radius:12px;font-size:13px;font-family:sans-serif;margin-top:8px;">
  <button onclick="ttsPlay()" title="Play"
    style="min-width:38px;height:38px;border-radius:50%;border:2px solid #2563eb;
           background:#2563eb;color:white;cursor:pointer;font-size:16px;flex-shrink:0;">&#9654;</button>
  <button onclick="window.speechSynthesis.cancel()" title="Stop"
    style="min-width:38px;height:38px;border-radius:50%;border:2px solid #ccc;
           background:white;color:#555;cursor:pointer;font-size:16px;flex-shrink:0;">&#9632;</button>
  <span style="flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;color:#555;">{preview}</span>
</div>
<script>
(function(){{
  var TEXT='{escaped}',LANG='{lang_code}';
  function pickVoice(l){{
    var vv=window.speechSynthesis.getVoices();
    for(var v of vv){{if(v.lang===l)return v;}}
    var p=l.split('-')[0];
    for(var v of vv){{if(v.lang.startsWith(p))return v;}}
    return null;
  }}
  window.ttsPlay=function(){{
    window.speechSynthesis.cancel();
    var u=new SpeechSynthesisUtterance(TEXT);
    var v=pickVoice(LANG)||pickVoice('en-IN');
    if(v){{u.voice=v;}} u.lang=v?v.lang:'en-IN'; u.rate=0.88; u.pitch=1.0;
    window.speechSynthesis.speak(u);
  }};
  window.speechSynthesis.onvoiceschanged=function(){{window.speechSynthesis.getVoices();}};
}})();
</script>""", height=66)

def get_display_name(k): return CROP_DATA["display_names"].get(k, k.replace("_"," ").title())
def get_crop_info(k): return CROP_DATA["info"].get(k.lower(),{"season":"—","water":"—","icon":"🌱"})

@st.cache_resource(show_spinner=False)
def load_models():
    return (pickle.load(open("model/crop_model.pkl","rb")),
            pickle.load(open("model/label_encoder.pkl","rb")))


# ═══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════
def display_top_recommendation(crop_key, crop_label, confidence, temp, humidity, rainfall, ph, N, P, K, district, source="soil"):
    crop_info = get_crop_info(crop_key)
    image_data, is_real = fetch_crop_image(crop_key, CROP_DATA)
    
    # Dynamic UX Text
    badge_text = T('top_rec') if source == "soil" else "🤖 AI Vision Identification"
    subtitle_text = f"{T('best_fit')} {district} — {T('best_fit2')}" if source == "soil" else f"Data provided for your scanned crop in {district}."

    st.markdown(f"""
    <div class="crop-card">
      <div class="badge">{badge_text} &nbsp;·&nbsp; {confidence:.1f}% confidence</div>
      <h2>{crop_info['icon']} {crop_label}</h2>
      <p>{subtitle_text}</p>
    </div>""", unsafe_allow_html=True)

    img_col, info_col = st.columns([1, 2])
    with img_col:
        st.image(image_data, use_container_width=True,
                 caption=T("real_photo") if is_real else f"{crop_info['icon']} {crop_label}")

    with info_col:
        st.markdown(
            f'<span class="metric-pill">📅 {crop_info["season"]}</span>'
            f'<span class="metric-pill">💧 {T("water_need")}: {crop_info["water"]}</span>'
            f'<span class="metric-pill">🌡️ {temp}°C</span>'
            f'<span class="metric-pill">💦 {humidity}% humidity</span>',
            unsafe_allow_html=True)
        st.markdown("")
        pct = int(confidence)
        st.markdown(f"""
        <div class="conf-bar-wrap">
          <div style="font-size:.82rem;color:#555;margin-bottom:5px;">{T('confidence')}: <strong>{confidence:.1f}%</strong></div>
          <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{pct}%;"></div></div>
        </div>""", unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f"**{T('why_crop')}**")
        st.markdown(f"{T('ai_matched')} **{crop_label}** {T('based_on')} {ph}, "
                    f"N={N}/P={P}/K={K}. {T('live_weather')} {district}: "
                    f"{temp}°C, {humidity}%, {rainfall} {T('exp_rainfall')} {T('hist_align')}")

        # TTS
        fert_preview   = calculate_fertilizer_prescription(crop_key, N, P, K, CROP_DATA)
        market_preview = get_market_forecast(crop_key, CROP_DATA)
        st.markdown(f"**{T('listen_btn')}**")
        render_tts_player(
            build_tts_summary(crop_label, fert_preview, market_preview,
                              lang=st.session_state.get("lang","en"),
                              crop_key=crop_key),
            lang=st.session_state.get("lang","en"))

def display_runner_ups(top_n_crops, top_n_probs, top_n):
    st.markdown(f"### 🌱 {T('top_n_recs')}")
    rec_cols = st.columns(min(top_n, 4))
    for i, col in enumerate(rec_cols[:top_n]):
        with col:
            nm   = get_display_name(top_n_crops[i])
            ci   = get_crop_info(top_n_crops[i])
            rank = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣"][i]
            pct_i = int(top_n_probs[i]*100)
            st.markdown(f"""
            <div style="background:{'rgba(37,99,235,.06)' if i==0 else 'rgba(0,0,0,.02)'};
                 border:1px solid {'rgba(37,99,235,.2)' if i==0 else 'rgba(0,0,0,.07)'};
                 border-radius:14px;padding:1rem;text-align:center;height:100%;">
              <div style="font-size:1.4rem;">{rank}</div>
              <div style="font-weight:600;font-size:.9rem;margin:.4rem 0;">{nm}</div>
              <div style="font-size:1.3rem;font-weight:700;color:{'#1e3a8a' if i==0 else '#444'};">{pct_i}%</div>
              <div style="font-size:.75rem;color:#888;margin-top:4px;">{ci['icon']} {ci['season']}</div>
              <div style="background:#eff6ff;border-radius:6px;height:6px;margin-top:8px;overflow:hidden;">
                <div style="background:#2563eb;height:6px;width:{pct_i}%;border-radius:6px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

def display_environmental_dashboard(temp, humidity, ph, rainfall, N, P, K, top_n_crops, top_n_probs):
    st.markdown(f'<h3 style="color: #0f172a;">{T("env_analysis")}</h3>', unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)

    def gauge(val, title, rng, color, steps):
        fig = go.Figure(go.Indicator(mode="gauge+number", value=val,
            title={"text":title,"font":{"size":13,"color":"#444"}},
            number={"font":{"size":26,"color":"#0f172a"}},
            gauge={"axis":{"range":rng,"tickcolor":"#888","tickfont":{"color":"#888"}},
                   "bar":{"color":color,"thickness":.25},
                   "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                   "steps":steps}))
        fig.update_layout(height=200, margin=dict(l=15,r=15,t=40,b=5),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    with d1: st.plotly_chart(gauge(temp,"Temperature °C",[0,50],"#e05252",
        [{"range":[0,20],"color":"#dbeafe"},{"range":[20,35],"color":"#dcfce7"},{"range":[35,50],"color":"#fee2e2"}]),
        use_container_width=True)
    with d2: st.plotly_chart(gauge(humidity,"Humidity %",[0,100],"#4a90d9",
        [{"range":[0,40],"color":"#f1f5f9"},{"range":[40,70],"color":"#dcfce7"},{"range":[70,100],"color":"#dbeafe"}]),
        use_container_width=True)
    with d3:
        pc = "#2563eb" if 5.5<=ph<=7.5 else "#e76f51"
        st.plotly_chart(gauge(ph,"Soil pH",[3,9],pc,
            [{"range":[3,5.5],"color":"#fee2e2"},{"range":[5.5,7.5],"color":"#dcfce7"},{"range":[7.5,9],"color":"#fef9c3"}]),
            use_container_width=True)
    with d4: st.plotly_chart(gauge(rainfall,"Rainfall mm",[0,500],"#4895ef",
        [{"range":[0,100],"color":"#fef9c3"},{"range":[100,250],"color":"#dcfce7"},{"range":[250,500],"color":"#dbeafe"}]),
        use_container_width=True)

    rc, bc = st.columns(2)
    with rc:
        fig = go.Figure(go.Scatterpolar(
            r=[N,P,K,N], theta=[T("nitrogen"), T("phosphorus"), T("potassium"), T("nitrogen")],
            fill="toself", line_color="#2563eb", fillcolor="rgba(37,99,235,.15)",
            mode="lines+markers", marker=dict(color="#2563eb",size=8)))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,max(150,N,P,K)+10], tickfont=dict(size=10, color="black")),
                angularaxis=dict(tickfont=dict(size=11, color="black"))
            ),
            showlegend=False, title={"text":T("npk_title"),"x":.5,"font":{"size":14,"color":"black"}},
            height=300, margin=dict(l=30,r=30,t=50,b=20),
            paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<div style="font-size:0.85rem; color:#444; padding:0 10px;">{T("npk_desc")}</div>', unsafe_allow_html=True)
    with bc:
        clabels = [get_display_name(c) for c in top_n_crops]
        cpcts   = [p*100 for p in top_n_probs]
        colors  = ["#1e3a8a" if i==0 else "#60a5fa" for i in range(len(clabels))]
        fig = go.Figure(go.Bar(x=cpcts, y=clabels, orientation="h",
            marker=dict(color=colors, cornerradius=6),
            text=[f"{c:.1f}%" for c in cpcts], textposition="outside",
            textfont=dict(size=12)))
        fig.update_layout(title={"text":"AI Confidence Scores","x":.5,"font":{"size":14}},
            xaxis=dict(range=[0,108],title="",showgrid=False,showticklabels=False),
            yaxis=dict(autorange="reversed"),height=300,
            margin=dict(l=10,r=50,t=50,b=20),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

def display_fertilizer_prescription(crop_key, N, P, K):
    st.markdown(f"### {T('fert_title')}")
    st.markdown(T("fert_desc"))
    fert = calculate_fertilizer_prescription(crop_key, N, P, K, CROP_DATA)

    if fert["all_optimal"]:
        st.success(T("fert_optimal"))
    else:
        req = fert["required"]
        f1, f2, f3 = st.columns(3)
        with f1:
            d = fert["deficit_N"]
            st.metric(T("nitrogen"), f"{N} kg/ha",
                      f"Need {req['N']} — Deficit: {d}",
                      delta_color="normal" if d==0 else "inverse")
        with f2:
            d = fert["deficit_P"]
            st.metric(T("phosphorus"), f"{P} kg/ha",
                      f"Need {req['P']} — Deficit: {d}",
                      delta_color="normal" if d==0 else "inverse")
        with f3:
            d = fert["deficit_K"]
            st.metric(T("potassium"), f"{K} kg/ha",
                      f"Need {req['K']} — Deficit: {d}",
                      delta_color="normal" if d==0 else "inverse")

        st.markdown('<div class="fert-card">', unsafe_allow_html=True)
        st.markdown(f"**{T('presc_header')}**")
        pc1, pc2, pc3 = st.columns(3)

        with pc1:
            if fert["urea_kg"] > 0:
                st.metric(T("urea_label"), f"{fert['urea_kg']} kg", T("kg_per_ha"))
            else:
                st.metric(T("urea_label"), T("no_deficit"))

        with pc2:
            if fert["dap_kg"] > 0:
                st.metric(T("dap_label"), f"{fert['dap_kg']} kg", T("kg_per_ha"))
            else:
                st.metric(T("dap_label"), T("no_deficit"))

        with pc3:
            if fert["mop_kg"] > 0:
                st.metric(T("mop_label"), f"{fert['mop_kg']} kg", T("kg_per_ha"))
            else:
                st.metric(T("mop_label"), T("no_deficit"))

        st.markdown('</div>', unsafe_allow_html=True)
    return fert

def display_market_economics(crop_key, crop_label):
    st.markdown(f"### {T('market_title')}")
    market = get_market_forecast(crop_key, CROP_DATA)

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric(T("market_price"),   f"Rs.{market['price_per_q']:,}", "/quintal")
    mc2.metric(T("market_yield"),   f"{market['yield_q_ha']} q",    T("per_ha"))
    mc3.metric(T("market_revenue"), f"Rs.{market['revenue']:,}",    T("per_ha"))
    mc4.metric(T("market_cost"),    f"Rs.{market['input_cost']:,}", T("per_ha"))
    mc5.metric(T("market_profit"),  f"Rs.{market['net_profit']:,}",
               f"ROI {market['roi_pct']}%",
               delta_color="normal" if market["net_profit"]>0 else "inverse")

    st.markdown('<div class="market-card">', unsafe_allow_html=True)
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=["relative","relative","total"],
        x=["Revenue","Input Cost","Net Profit"],
        y=[market["revenue"], -market["input_cost"], 0],
        connector={"line":{"color":"rgba(0,0,0,.15)","width":1}},
        increasing={"marker":{"color":"#2563eb","line":{"color":"#1e3a8a","width":1}}},
        decreasing={"marker":{"color":"#e05252","line":{"color":"#c0392b","width":1}}},
        totals={"marker":{"color":"#2463ae","line":{"color":"#1a4f8a","width":1}}},
        text=[f"Rs.{market['revenue']:,}", f"-Rs.{market['input_cost']:,}", f"Rs.{market['net_profit']:,}"],
        textposition="outside", textfont=dict(size=12)))
    fig.update_layout(
        title={"text":f"Per Hectare Economics — {crop_label}","x":.5,"font":{"size":14}},
        yaxis=dict(title="INR (Rs.)", showgrid=True, gridcolor="rgba(0,0,0,.06)"),
        height=320, margin=dict(l=20,r=20,t=55,b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"ℹ️ {T('market_note')}")
    st.markdown('</div>', unsafe_allow_html=True)
    return market


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3a8a,#2563eb);padding:18px 16px;
         border-radius:12px;margin-bottom:12px;text-align:center;">
      <div style="font-size:28px;margin-bottom:4px;">🌾</div>
      <div style="color:white;font-size:16px;font-weight:600;letter-spacing:.5px;">Assam Crop Advisor</div>
      <div style="color:rgba(255,255,255,.6);font-size:11px;margin-top:2px;">Right crop, right time, maximum yield.</div>
    </div>""", unsafe_allow_html=True)

    st.radio(T("lang_toggle"), options=["en","as"],
             format_func=lambda x:"🇬🇧 English" if x=="en" else "🇮🇳 অসমীয়া",
             horizontal=True, key="lang")
    st.divider()

    with st.expander(f"📍 {T('location_hdr')}", expanded=True):
        _ASSAM_LOCATIONS = [
            "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", 
            "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", 
            "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", 
            "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", 
            "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", 
            "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong",
            "Guwahati", "Silchar", "Tezpur", "Diphu"
        ]
        district = st.selectbox(T("district"), options=sorted(_ASSAM_LOCATIONS), index=sorted(_ASSAM_LOCATIONS).index("Guwahati"),
                                  help="Used to fetch live temperature & humidity")

    with st.expander(f"⚙️ {T('input_mode_hdr')}", expanded=True):
        input_mode = st.radio(T("input_mode"), [T("simple"), T("advanced")], label_visibility="collapsed")

    with st.expander(f"📊 {T('display_opts')}", expanded=False):
        show_dashboard = st.toggle(T("show_dash"), value=True)
        show_history   = st.toggle(T("show_history"), value=False)
        top_n          = st.slider(T("num_recs"), 3, 7, 3)

    st.divider()

    with st.expander(f"📷 {T('cam_header')}", expanded=False):
        use_cam = st.toggle(T("cam_toggle"), value=False)
        cam_img = None
        if use_cam:
            cam_img = st.camera_input(T("cam_take"))
        
        up_img = st.file_uploader(
            T("cam_upload"), type=["jpg","jpeg","png","webp"], key="cam_upload_widget")
        
        final_img = cam_img or up_img
        if final_img:
            img_bytes = final_img.getvalue()
            import hashlib
            img_hash = hashlib.md5(img_bytes).hexdigest()
            
            # Only call AI if it's a new image
            if st.session_state.get("last_img_hash") != img_hash:
                with st.spinner(T("cam_detecting")):
                    result = identify_crop_ai(img_bytes, CROP_DATA)
                st.session_state["last_img_hash"] = img_hash
                st.session_state["last_img_result"] = result
                
                if result.get("confidence", 0) > 0 and result.get("crop_key") != "unknown":
                    st.session_state["detected_crop"] = result["crop_key"]
                    st.session_state["detected_conf"] = result["confidence"]
                    st.session_state["auto_run"] = True
            
            result = st.session_state.get("last_img_result", {})
            if result.get("confidence", 0) > 0 and result.get("crop_key") != "unknown":
                st.success(f"{T('cam_detected')}: **{result['display_name']}** ({result['confidence']}%)")
                if result.get("notes"):
                    st.info(result["notes"])
            else:
                st.warning(result.get("notes", T("cam_error")))


# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADED CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

/* ── Main crop card ── */
.crop-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 20px; padding: 2rem 2.25rem; color: #0f172a; margin: 1rem 0;
    border: 1px solid #bae6fd;
    box-shadow: 0 4px 20px rgba(0,0,0,.05);
    position: relative; overflow: hidden;
}
.crop-card::before {
    content:""; position:absolute; top:-60px; right:-60px;
    width:200px; height:200px; border-radius:50%;
    background:rgba(37,99,235,.03);
}
.crop-card::after {
    content:""; position:absolute; bottom:-80px; left:30%;
    width:300px; height:300px; border-radius:50%;
    background:rgba(37,99,235,.02);
}
.crop-card h2 { margin:0 0 .35rem 0; font-size:2.2rem; font-weight:700; line-height:1.2; }
.crop-card p  { margin:0; opacity:.75; font-size:.92rem; }

/* ── Metric pills ── */
.metric-pill {
    display:inline-flex; align-items:center; gap:.4rem;
    background:rgba(37,99,235,.10); border:1px solid rgba(37,99,235,.22);
    border-radius:30px; padding:.4rem 1rem;
    font-size:.82rem; font-weight:500; margin:3px 2px;
    transition: background .2s;
}
.metric-pill:hover { background:rgba(37,99,235,.18); }

/* ── Section cards ── */
.section-card {
    background: var(--background-color, #ffffff);
    border: 1px solid rgba(0,0,0,.07);
    border-radius: 16px; padding: 1.25rem 1.5rem; margin: .75rem 0;
}

/* ── Fert & market cards ── */
.fert-card {
    background:rgba(139,69,19,.05); border-left:3px solid #c0722a;
    border-radius:0 14px 14px 0; padding:1.25rem 1.5rem; margin:.75rem 0;
}
.market-card {
    background:rgba(0,70,140,.04); border-left:3px solid #2463ae;
    border-radius:0 14px 14px 0; padding:1.25rem 1.5rem; margin:.75rem 0;
}

/* ── Alert banner ── */
.alert-banner {
    border-left:3px solid #e6a817;
    background:linear-gradient(90deg,rgba(230,168,23,.08),transparent);
    border-radius:0 10px 10px 0; padding:.8rem 1.1rem; font-size:.88rem; margin:.5rem 0;
}

/* ── Stat row inside market card ── */
.stat-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.5rem 0; border-bottom:1px solid rgba(0,0,0,.06);
    font-size:.88rem;
}
.stat-row:last-child { border-bottom:none; }
.stat-label { color:#666; }
.stat-value { font-weight:600; color:#1e3a8a; }
.stat-value.profit { color:#1a6b3c; font-size:1.05rem; }
.stat-value.cost   { color:#b03a2e; }

/* ── Confidence bar ── */
.conf-bar-wrap { margin-top:8px; }
.conf-bar-bg { background:#eff6ff; border-radius:8px; height:10px; overflow:hidden; }
.conf-bar-fill { background:linear-gradient(90deg,#2563eb,#60a5fa); height:10px; border-radius:8px; transition:width .8s ease; }

/* ── Sidebar tweaks ── */
section[data-testid="stSidebar"] > div { padding-top: 1rem !important; }

/* ── Hide Streamlit footer ── */
footer { visibility:hidden; }
#MainMenu { visibility:hidden; }
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="padding:.5rem 0 1.5rem;">
  <h1 style="font-size:1.9rem;font-weight:700;margin:0 0 .25rem;">{T('title')}</h1>
  <p style="color:#666;margin:0;font-size:.95rem;">{T('subtitle')}</p>
</div>""", unsafe_allow_html=True)

st.markdown(f"### {T('soil_header')}")
simple_mode = T("simple") in input_mode

if simple_mode:
    col1, col2 = st.columns(2)
    with col1:
        soil_type = st.selectbox(T("soil_type"), list(soil_properties.keys()), format_func=T)
        ph_v = soil_properties[soil_type]['ph']
        st.markdown(f'<div style="font-size:.82rem;color:#666;margin-top:4px;">'
                    f'pH {ph_v} &nbsp;·&nbsp; N={soil_properties[soil_type]["N"]} '
                    f'&nbsp;·&nbsp; P={soil_properties[soil_type]["P"]} '
                    f'&nbsp;·&nbsp; K={soil_properties[soil_type]["K"]}</div>', unsafe_allow_html=True)
    with col2:
        season = st.selectbox(T("season"), list(season_rainfall.keys()), format_func=T)
        st.markdown(f'<div style="font-size:.82rem;color:#666;margin-top:4px;">'
                    f'{T("exp_rainfall_prefix")} {season_rainfall[season]} {T("exp_rainfall_suffix")}</div>', unsafe_allow_html=True)

    detected = st.session_state.get("detected_crop")
    if detected and detected != "unknown":
        st.info(f"{T('cam_pre_filled')} **{get_display_name(detected)}** — switch to Advanced Mode to use exact values.")

    N  = soil_properties[soil_type]["N"]
    P  = soil_properties[soil_type]["P"]
    K  = soil_properties[soil_type]["K"]
    ph = soil_properties[soil_type]["ph"]
    rainfall = season_rainfall[season]
else:
    st.info("Enter your soil lab test results. Weather is fetched automatically.")
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
    if npk_sum > 0 and (N/npk_sum) > 0.6:
        st.markdown('<div class="alert-banner">⚠️ High nitrogen — may favour leafy crops over fruiting ones.</div>', unsafe_allow_html=True)
    if ph < 4.5:
        st.markdown('<div class="alert-banner">⚠️ Highly acidic (pH < 4.5). Consider liming before planting.</div>', unsafe_allow_html=True)
    elif ph > 8.0:
        st.markdown('<div class="alert-banner">⚠️ Alkaline soil (pH > 8). May limit nutrient uptake.</div>', unsafe_allow_html=True)

st.markdown("")
predict_btn = st.button(T("predict_btn"), type="primary", use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
if predict_btn or st.session_state.pop("auto_run", False):
    try:
        with st.spinner(T("fetching")):
            try:
                rf_model, label_encoder = load_models()
            except Exception as e:
                logger.error(f"Failed to load models: {e}")
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
            
            # ─── Vision Override ───
            # If a crop was just detected via camera, force it to be the top result
            detected_crop = st.session_state.get("detected_crop")
            if detected_crop and detected_crop != "unknown":
                # Move detected crop to index 0 if it exists in our supported list
                if detected_crop in top_n_crops:
                    idx = list(top_n_crops).index(detected_crop)
                    # Swap with top result
                    top_n_crops[0], top_n_crops[idx] = top_n_crops[idx], top_n_crops[0]
                    top_n_probs[0], top_n_probs[idx] = top_n_probs[idx], top_n_probs[0]
                else:
                    # If not in top N, replace the first one
                    top_n_crops[0] = detected_crop
                    top_n_probs[0] = st.session_state.get("detected_conf", 99.0) / 100.0
            
            best_crop = top_n_crops[0]
            logger.info(f"Prediction generated for {district}: {best_crop} ({top_n_probs[0]*100:.1f}%)")

        st.success(T("analysis_done"))
        st.divider()

        best_crop  = top_n_crops[0]
        best_label = get_display_name(best_crop)
        best_conf  = top_n_probs[0] * 100

        # 1. Top recommendation card
        rec_source = "vision" if st.session_state.get("detected_crop") == best_crop else "soil"
        display_top_recommendation(best_crop, best_label, best_conf, temp, humidity, rainfall, ph, N, P, K, district, source=rec_source)
        st.divider()

        # 2. Runner-ups
        display_runner_ups(top_n_crops, top_n_probs, top_n)
        st.divider()

        # 3. Environmental dashboard
        if show_dashboard:
            display_environmental_dashboard(temp, humidity, ph, rainfall, N, P, K, top_n_crops, top_n_probs)
            st.divider()

        # 4. Fertilizer prescription
        fert = display_fertilizer_prescription(best_crop, N, P, K)
        st.divider()

        # 5. Market forecast
        market = display_market_economics(best_crop, best_label)
        st.divider()

        # 6. Analytics & History
        if show_history:
            st.divider()
            st.markdown(f"### 📊 {T('history_title')}")
            
            # --- NEW: Trends Dashboard ---
            with st.expander("🌍 Assam Agriculture Trends (Community Data)", expanded=True):
                analytics = get_regional_analytics()
                
                tcol1, tcol2 = st.columns(2)
                with tcol1:
                    # Top Crops Chart
                    if analytics["top_crops"]:
                        labels = [c["crop_name"] for c in analytics["top_crops"]]
                        counts = [c["count"] for c in analytics["top_crops"]]
                        fig = go.Figure(go.Bar(x=labels, y=counts, marker_color="#2563eb"))
                        fig.update_layout(title="Most Searched Crops", height=300, 
                                          margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Not enough data for crop trends.")
                        
                with tcol2:
                    # District Activity
                    if analytics["district_stats"]:
                        df_dist = pd.DataFrame(analytics["district_stats"])
                        st.markdown("**Activity by District**")
                        st.dataframe(df_dist, use_container_width=True, hide_index=True)
                    else:
                        st.info("Not enough data for district stats.")
            
            # --- Existing History Table ---
            st.markdown("#### Recent Personal Predictions")
            # Save the current prediction to DB
            save_report(district, best_crop, best_label, best_conf, temp, humidity, ph, rainfall, N, P, K, st.session_state.lang)
            
            # Fetch and display history from DB
            history_data = get_all_reports()
            if history_data:
                df_history = pd.DataFrame(history_data)
                # Cleanup display columns for simple view
                display_cols = ["timestamp", "district", "crop_name", "confidence", "temp", "humidity"]
                st.dataframe(df_history[display_cols], use_container_width=True, hide_index=True)
                
                if st.button(T("clear_history")):
                    clear_all_reports()
                    st.rerun()
            else:
                st.info("No history found in database.")

        # 7. PDF export
        st.markdown(f"### {T('export_title')}")
        st.markdown(T("export_desc"))
        pdf_bytes = create_pdf_report(
            district, best_label, best_conf, temp, humidity, ph,
            rainfall, N, P, K, fert, market, UI_TEXT,
            lang=st.session_state.get("lang","en"))
        st.download_button(label=T("download_pdf"), data=pdf_bytes,
            file_name=f"{district}_Crop_Report_{datetime.date.today()}.pdf",
            mime="application/pdf", use_container_width=True)
        st.divider()

        # 8. Input summary
        with st.expander(T("input_summary")):
            summary = {
                T("district_lbl"):district, T("temperature"):temp,
                T("humidity"):humidity, T("nitrogen"):N,
                T("phosphorus"):P, T("potassium"):K,
                T("soil_ph"):ph, T("rainfall_mm"):rainfall}
            st.table(pd.DataFrame.from_dict(summary, orient="index", columns=[T("value")]))

    except Exception as e:
        logger.exception(f"Critical error in prediction loop: {e}")
        st.error("An unexpected error occurred. Our team has been notified.")
        st.info("Check the logs directory for details.")
