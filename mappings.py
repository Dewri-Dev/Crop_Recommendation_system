# mappings.py (Add this to the bottom)

# Dictionary linking crop names to image URLs
crop_images = {
    "assam_tea": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Tea_leaves_at_a_plantation_in_Assam.jpg/800px-Tea_leaves_at_a_plantation_in_Assam.jpg",
    "joha_rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=500&q=60",
    "bhut_jolokia": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Bhut_Jolokia.jpg/500px-Bhut_Jolokia.jpg",
    # Add your other crops here...
    "default": "https://images.unsplash.com/photo-1592982537447-6f204c356e18?auto=format&fit=crop&w=500&q=60" # A nice generic farm picture
}

# Estimate base soil parameters based on general soil types in Assam
soil_properties = {
    "Loamy (Alluvial)": {"N": 70, "P": 45, "K": 40, "ph": 6.5}, # Common in Brahmaputra valley
    "Sandy":            {"N": 30, "P": 25, "K": 20, "ph": 5.5}, # Riverbanks
    "Clay":             {"N": 50, "P": 50, "K": 60, "ph": 7.0},
    "Red Soil":         {"N": 40, "P": 30, "K": 35, "ph": 5.8}  # Hilly areas (Karbi Anglong)
}

# Estimate average rainfall based on the current season (in mm)
season_rainfall = {
    "Pre-Monsoon (Mar - May)": 150.0,
    "Monsoon (Jun - Sep)": 350.0,
    "Post-Monsoon (Oct - Nov)": 80.0,
    "Winter (Dec - Feb)": 20.0
}

