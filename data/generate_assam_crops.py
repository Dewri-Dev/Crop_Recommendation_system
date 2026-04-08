import pandas as pd
import random
import os

# Define the ideal growing conditions for 17 local Assamese crops
# Format: (Min, Max) for N, P, K, Temperature (°C), Humidity (%), pH, Rainfall (mm)
crop_profiles = {
    "bora_rice":     {"N": (60, 90), "P": (40, 60), "K": (38, 45), "temp": (24.0, 32.0), "hum": (80.0, 90.0), "ph": (5.5, 6.5), "rain": (200.0, 280.0)},
    "chokuwa_rice":  {"N": (60, 85), "P": (40, 55), "K": (38, 45), "temp": (23.0, 31.0), "hum": (80.0, 88.0), "ph": (5.5, 6.8), "rain": (210.0, 270.0)},
    "bao_rice":      {"N": (50, 80), "P": (30, 50), "K": (30, 40), "temp": (25.0, 34.0), "hum": (85.0, 95.0), "ph": (5.0, 6.5), "rain": (300.0, 450.0)}, # Deep water
    "komal_saul":    {"N": (65, 90), "P": (45, 60), "K": (40, 50), "temp": (24.0, 30.0), "hum": (80.0, 85.0), "ph": (5.5, 6.5), "rain": (200.0, 260.0)},
    "thekera":       {"N": (40, 60), "P": (30, 50), "K": (40, 60), "temp": (22.0, 32.0), "hum": (70.0, 85.0), "ph": (5.0, 6.5), "rain": (250.0, 350.0)},
    "bogori":        {"N": (30, 50), "P": (20, 40), "K": (30, 50), "temp": (25.0, 35.0), "hum": (50.0, 70.0), "ph": (5.5, 7.5), "rain": (100.0, 200.0)}, # Hardy, tolerates less rain
    "amlokhi":       {"N": (30, 50), "P": (20, 40), "K": (30, 50), "temp": (20.0, 35.0), "hum": (60.0, 75.0), "ph": (6.0, 8.0), "rain": (150.0, 250.0)},
    "jalpai":        {"N": (40, 60), "P": (30, 50), "K": (40, 60), "temp": (20.0, 32.0), "hum": (70.0, 85.0), "ph": (5.5, 6.5), "rain": (200.0, 300.0)},
    "areca_nut":     {"N": (80, 110),"P": (40, 60), "K": (80, 120),"temp": (20.0, 30.0), "hum": (75.0, 90.0), "ph": (5.0, 6.5), "rain": (200.0, 350.0)},
    "betel_leaf":    {"N": (90, 120),"P": (50, 70), "K": (80, 110),"temp": (20.0, 30.0), "hum": (85.0, 95.0), "ph": (5.5, 7.0), "rain": (220.0, 300.0)}, # High humidity/shade
    "manimuni":      {"N": (20, 40), "P": (15, 30), "K": (20, 40), "temp": (20.0, 30.0), "hum": (80.0, 95.0), "ph": (5.5, 7.0), "rain": (200.0, 300.0)}, # Swampy/Moist
    "kosu":          {"N": (40, 60), "P": (30, 50), "K": (60, 80), "temp": (20.0, 30.0), "hum": (75.0, 90.0), "ph": (5.5, 6.5), "rain": (180.0, 280.0)}, # Colocasia loves moisture
    "bamboo_shoot":  {"N": (80, 120),"P": (30, 50), "K": (60, 90), "temp": (20.0, 32.0), "hum": (75.0, 90.0), "ph": (5.0, 6.5), "rain": (200.0, 400.0)},
    "local_pumpkin": {"N": (40, 60), "P": (50, 70), "K": (60, 80), "temp": (22.0, 30.0), "hum": (65.0, 80.0), "ph": (6.0, 7.0), "rain": (150.0, 220.0)},
    "local_brinjal": {"N": (50, 70), "P": (40, 60), "K": (50, 70), "temp": (22.0, 32.0), "hum": (65.0, 80.0), "ph": (5.5, 6.8), "rain": (150.0, 200.0)},
    "local_beans":   {"N": (10, 30), "P": (50, 70), "K": (40, 60), "temp": (18.0, 28.0), "hum": (60.0, 75.0), "ph": (6.0, 7.0), "rain": (100.0, 180.0)}, # Legumes fix their own N
    "apong_rice":    {"N": (60, 85), "P": (40, 55), "K": (38, 45), "temp": (24.0, 32.0), "hum": (80.0, 88.0), "ph": (5.5, 6.5), "rain": (200.0, 270.0)}  # Distinct label for Apong variety
}

data = []

# Generate exactly 100 rows for each crop to maintain dataset balance
for crop_name, conditions in crop_profiles.items():
    for _ in range(100):
        row = {
            'N': random.randint(*conditions["N"]),
            'P': random.randint(*conditions["P"]),
            'K': random.randint(*conditions["K"]),
            'temperature': round(random.uniform(*conditions["temp"]), 2),
            'humidity': round(random.uniform(*conditions["hum"]), 2),
            'ph': round(random.uniform(*conditions["ph"]), 2),
            'rainfall': round(random.uniform(*conditions["rain"]), 2),
            'label': crop_name
        }
        data.append(row)

# Convert to a Pandas DataFrame
new_crops_df = pd.DataFrame(data)

# Define the path to your CSV (Ensure this matches your folder structure)
csv_path = 'data/Crop_recommendation.csv'

# Check if file exists, then append
if os.path.exists(csv_path):
    new_crops_df.to_csv(csv_path, mode='a', header=False, index=False)
    print(f"✅ Successfully added 1,700 new rows (100 for each of the 17 crops) to {csv_path}!")
else:
    print(f"❌ Error: Could not find {csv_path}. Make sure you are running this from the project root directory.")