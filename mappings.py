"""
mappings.py — Static reference data for the Assam Crop Recommendation System
"""

# ─── Soil Properties ──────────────────────────────────────────────────────────
# Estimated NPK ratios and pH for common soil types found across Assam.
# Sources: ICAR soil health card averages for NE India.

soil_properties = {
    # Major river-valley soils
    "Loamy / Alluvial":     {"N": 70,  "P": 45, "K": 40, "ph": 6.5, "region": "Brahmaputra & Barak valley"},
    "Sandy / Riverbank":    {"N": 30,  "P": 25, "K": 20, "ph": 5.5, "region": "Riverbanks, chars"},
    "Clay":                 {"N": 50,  "P": 50, "K": 60, "ph": 7.0, "region": "Low-lying paddy areas"},
    "Red Laterite":         {"N": 40,  "P": 30, "K": 35, "ph": 5.8, "region": "Karbi Anglong, NC Hills"},

    # Tea-growing & hilly soils
    "Tea Garden Soil":      {"N": 55,  "P": 20, "K": 25, "ph": 4.8, "region": "Upper Assam tea belts"},
    "Hill / Forest Loam":   {"N": 60,  "P": 35, "K": 45, "ph": 5.2, "region": "Bodoland, Dima Hasao"},

    # Waterlogged / beel areas
    "Peaty / Waterlogged":  {"N": 35,  "P": 15, "K": 20, "ph": 5.0, "region": "Beel & wetland periphery"},

    # Sandy-loam (common market-garden soil)
    "Sandy Loam":           {"N": 55,  "P": 38, "K": 32, "ph": 6.2, "region": "Market-garden belts"},
}


# ─── Season Rainfall ──────────────────────────────────────────────────────────
# Average expected rainfall (mm) per season in Assam.
# Figures based on IMD climatological normals for the state.

season_rainfall = {
    "Pre-Monsoon  (Mar – May)":  150.0,
    "Monsoon      (Jun – Sep)":  350.0,
    "Post-Monsoon (Oct – Nov)":   80.0,
    "Winter       (Dec – Feb)":   20.0,
}


# ─── Crop Image URL Overrides ────────────────────────────────────────────────
# Only list crops where a generic search term is ambiguous or returns wrong results.
# For all other crops, app.py fetches from Unsplash automatically using the crop name.
# Key: lowercase crop name matching label_encoder output.

crop_images: dict[str, str] = {
    # Assam-specific crops that generic search may not find correctly
    "amlokhi":         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Phyllanthus_emblica.jpg/640px-Phyllanthus_emblica.jpg",
    "amla":            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Phyllanthus_emblica.jpg/640px-Phyllanthus_emblica.jpg",
    "bhut_jolokia":    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Bhut_Jolokia.jpg/500px-Bhut_Jolokia.jpg",
    "joha_rice":       "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Rice_p1160004.jpg/640px-Rice_p1160004.jpg",
    "assam_tea":       "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Tea_leaves_at_a_plantation_in_Assam.jpg/800px-Tea_leaves_at_a_plantation_in_Assam.jpg",
    "elephant_foot_yam": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Amorphophallus_paeoniifolius.jpg/640px-Amorphophallus_paeoniifolius.jpg",
    # Generic fallback (used only if Unsplash also fails)
    "default":         "https://placehold.co/800x600/2E8B57/white?text=Crop",
}


# ─── Soil Descriptions ────────────────────────────────────────────────────────
# Short plain-English notes shown to farmers in Simple Mode.

soil_descriptions: dict[str, str] = {
    "Loamy / Alluvial":      "Rich, well-draining soil. Good for most crops. Common near rivers.",
    "Sandy / Riverbank":     "Loose, low-nutrient soil. Drains quickly. Good for root vegetables.",
    "Clay":                  "Heavy, moisture-retaining soil. Suits paddy. Can waterlog easily.",
    "Red Laterite":          "Acidic, iron-rich soil common in hills. Good for tea, pineapple.",
    "Tea Garden Soil":       "Very acidic, well-leached. Ideal for tea. Needs fertiliser for other crops.",
    "Hill / Forest Loam":    "Moist, humus-rich. Suits vegetables, ginger, turmeric.",
    "Peaty / Waterlogged":   "High organic matter, low oxygen. Best drained before planting.",
    "Sandy Loam":            "Balanced texture. Easy to work. Suits vegetables and cereals.",
}


# ─── Season Descriptions ──────────────────────────────────────────────────────
season_descriptions: dict[str, str] = {
    "Pre-Monsoon  (Mar – May)":  "Hot & dry. Good for summer vegetables and early kharif sowing.",
    "Monsoon      (Jun – Sep)":  "High rainfall. Peak kharif season — rice, jute, maize.",
    "Post-Monsoon (Oct – Nov)":  "Retreating rains. Good for rabi sowing and transplanting.",
    "Winter       (Dec – Feb)":  "Cool & dry. Ideal for wheat, mustard, pulses.",
}


# ─── Helper Utilities ─────────────────────────────────────────────────────────

def get_soil_props(soil_type: str) -> dict:
    """Return NPK, pH, and region for a given soil type key."""
    return soil_properties.get(soil_type, soil_properties["Loamy / Alluvial"])


def get_crop_image(crop_name: str) -> str:
    """
    Return image URL for a crop name.
    Falls back to 'default' if the crop is not in the dictionary.
    """
    key = crop_name.lower().replace(" ", "_")
    return crop_images.get(key, crop_images["default"])


def get_soil_description(soil_type: str) -> str:
    return soil_descriptions.get(soil_type, "")


def get_season_description(season: str) -> str:
    return season_descriptions.get(season, "")
