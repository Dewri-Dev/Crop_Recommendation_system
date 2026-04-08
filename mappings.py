# mappings.py

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