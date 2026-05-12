import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "data/history.db"

DISTRICTS = ["Guwahati", "Dibrugarh", "Jorhat", "Silchar", "Tezpur", "Nagaon", "Tinsukia"]
CROPS = [
    ("rice", "Rice"), ("maize", "Maize"), ("jute", "Jute"), 
    ("assam_tea", "Assam Tea"), ("banana", "Banana"), ("coconut", "Coconut")
]

def seed_database():
    print(f"🌱 Seeding database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist (safety first)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            district TEXT,
            crop_key TEXT,
            crop_name TEXT,
            confidence REAL,
            temp REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            language TEXT
        )
    ''')

    # Generate 50 random reports
    for _ in range(50):
        district = random.choice(DISTRICTS)
        crop_key, crop_name = random.choice(CROPS)
        conf = random.uniform(85.0, 100.0)
        temp = random.uniform(20.0, 35.0)
        hum = random.uniform(50.0, 90.0)
        ph = random.uniform(5.5, 7.5)
        rain = random.uniform(100.0, 400.0)
        n = random.randint(20, 120)
        p = random.randint(20, 120)
        k = random.randint(20, 120)
        
        # Random date in the last 30 days
        days_ago = random.randint(0, 30)
        ts = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO reports (timestamp, district, crop_key, crop_name, confidence, temp, humidity, ph, rainfall, nitrogen, phosphorus, potassium, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ts, district, crop_key, crop_name, conf, temp, hum, ph, rain, n, p, k, "en"))

    conn.commit()
    conn.close()
    print("✅ Seeded 50 new reports into the database.")

if __name__ == "__main__":
    seed_database()
