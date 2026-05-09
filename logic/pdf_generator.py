import os, urllib.request, datetime
from fpdf import FPDF

def _ensure_unicode_font():
    fp = "NotoSans-Regular.ttf"
    if not os.path.exists(fp):
        try:
            urllib.request.urlretrieve(
                "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf", fp)
        except Exception:
            pass
    return fp

def _pdf_safe(text):
    """Strip/replace anything Helvetica (Latin-1) cannot render."""
    subs = {"Rs.": "Rs.", "–": "-", "—": "-", "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'}
    for src, dst in subs.items():
        text = text.replace(src, dst)
    return "".join(c for c in text if ord(c) < 256 and c.isprintable()).strip()

def create_pdf_report(district, crop_name, confidence, temp, humidity, ph,
                      rainfall, N, P, K, fert, market, translations, lang="en"):
    t = translations.get(lang, translations["en"])
    pdf = FPDF()
    pdf.add_page()
    
    if lang == "as":
        fp = _ensure_unicode_font()
        if os.path.exists(fp):
            pdf.add_font("NotoSans", "", fp)
            pdf.add_font("NotoSans", "B", fp)
            FN = FB = "NotoSans"
            def S(x): return x  # NotoSans handles Unicode
        else:
            FN = FB = "Helvetica"
            def S(x): return _pdf_safe(str(x))
    else:
        FN = FB = "Helvetica"
        def S(x): return _pdf_safe(str(x))

    def sn(sz=12): pdf.set_font(FN, size=sz)
    def sb(sz=12): pdf.set_font(FB, style="B" if lang == "en" else "", size=sz)

    sb(20); pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 15, S(t["pdf_report"]), ln=True, align='C'); pdf.ln(3)
    
    sn(12); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, S(f"{t['pdf_date']}: {datetime.date.today().strftime('%B %d, %Y')}"), ln=True)
    pdf.cell(0, 10, S(f"{t['pdf_location']}: {district.title()}, Assam"), ln=True); pdf.ln(3)
    
    sb(14); pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, S(f"{t['pdf_top_crop']}: {crop_name} ({confidence:.1f}% confidence)"), ln=True); pdf.ln(3)
    
    sb(12); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, S(f"{t['pdf_env']}:"), ln=True); sn(12)
    for lbl, val in [(t['temperature'], f"{temp} C"), (t['humidity'], f"{humidity} %"),
                    (t['rainfall_mm'], f"{rainfall} mm"), (t['soil_ph'], str(ph)),
                    ("N / P / K", f"{N} | {P} | {K}")]:
        pdf.cell(0, 8, S(f"  - {lbl}: {val}"), ln=True)
    pdf.ln(4)
    
    sb(12); pdf.set_text_color(139, 69, 19)
    pdf.cell(0, 10, S(f"{t['pdf_fert']}:"), ln=True); sn(12); pdf.set_text_color(0, 0, 0)
    if fert["all_optimal"]:
        pdf.cell(0, 8, S(f"  [OK] {t['fert_optimal']}"), ln=True)
    else:
        for lbl, qty in [(t['add_urea'], fert['urea_kg']), (t['add_dap'], fert['dap_kg']), (t['add_mop'], fert['mop_kg'])]:
            if qty > 0:
                pdf.cell(0, 8, S(f"  - {lbl}: {qty} {t['kg_per_ha']}"), ln=True)
    pdf.ln(4)
    
    sb(12); pdf.set_text_color(0, 70, 140)
    pdf.cell(0, 10, S(f"{t['pdf_market']}:"), ln=True); sn(12); pdf.set_text_color(0, 0, 0)
    for lbl, val in [(t['market_price'], f"Rs. {market['price_per_q']:,} / quintal"),
                    (t['market_yield'], f"{market['yield_q_ha']} quintals"),
                    (t['market_revenue'], f"Rs. {market['revenue']:,}"),
                    (t['market_cost'], f"Rs. {market['input_cost']:,}"),
                    (t['market_profit'], f"Rs. {market['net_profit']:,} (ROI: {market['roi_pct']}%)")]:
        pdf.cell(0, 8, S(f"  - {lbl}: {val}"), ln=True)
    
    pdf.ln(10); sn(10); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, S(t["pdf_footer"]), align='C')
    
    return bytes(pdf.output())
