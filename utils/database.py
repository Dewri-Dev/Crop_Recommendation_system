import sqlite3
import os
from datetime import datetime
from utils.logger import logger

DB_PATH = "data/history.db"

def init_db():
    """Initializes the database and creates the reports table if it doesn't exist."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")

def save_report(district, crop_key, crop_name, confidence, temp, humidity, ph, rainfall, N, P, K, lang):
    """Saves a new recommendation report to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reports (district, crop_key, crop_name, confidence, temp, humidity, ph, rainfall, nitrogen, phosphorus, potassium, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (district, crop_key, crop_label_helper(crop_name), confidence, temp, humidity, ph, rainfall, N, P, K, lang))
        conn.commit()
        conn.close()
        logger.info(f"Report saved to database for {district}: {crop_key}")
    except Exception as e:
        logger.exception(f"Failed to save report to database: {e}")

def crop_label_helper(val):
    # Ensure we store strings, not complex objects if any
    return str(val)

def get_all_reports(limit=50):
    """Retrieves recent reports from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Use Row factory for dict-like access
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        reports = [dict(row) for row in rows]
        conn.close()
        return reports
    except Exception as e:
        logger.exception(f"Failed to fetch reports from database: {e}")
        return []

def clear_all_reports():
    """Clears all reports from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM reports')
        conn.commit()
        conn.close()
        logger.info("All database reports cleared.")
    except Exception as e:
        logger.exception(f"Failed to clear database reports: {e}")

def get_regional_analytics():
    """Performs complex SQL aggregation to find trends."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Top Crops Overall
        cursor.execute('''
            SELECT crop_name, COUNT(*) as count 
            FROM reports 
            GROUP BY crop_name 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        top_crops = [dict(row) for row in cursor.fetchall()]

        # 2. Activity by District
        cursor.execute('''
            SELECT district, COUNT(*) as count 
            FROM reports 
            GROUP BY district 
            ORDER BY count DESC
        ''')
        district_stats = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return {"top_crops": top_crops, "district_stats": district_stats}
    except Exception as e:
        logger.exception(f"Analytics query failed: {e}")
        return {"top_crops": [], "district_stats": []}
