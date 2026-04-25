# 🌾 Assam Crop Advisor (v4.0)
### AI-Powered Precision Agriculture for Northeastern India

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![ML](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-success?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Project Overview
Agriculture is the backbone of Assam's economy, yet many farmers struggle with suboptimal yields due to unpredictable climate patterns and lack of scientific soil analysis. **Assam Crop Advisor** is a professional prototype designed to bridge the gap between complex agronomical data and field-level decision making.

By leveraging a **Random Forest Machine Learning model** and **Real-Time Weather APIs**, this system provides farmers with accurate crop recommendations, fertilizer prescriptions, and economic forecasts—all through a highly accessible, multilingual interface.

---

## ✨ Core Features

### 🧠 Intelligent Recommendation
*   **Dual Input Modes:** 
    *   **Simple Mode:** Select soil type (Loamy, Clay, etc.) and season; NPK values are auto-populated based on Assam's regional soil mappings.
    *   **Advanced Mode:** Input exact soil lab results (N, P, K, pH) for precision analysis.
*   **Live Weather Sync:** Automatically fetches real-time temperature and humidity based on the selected Assam district using OpenWeatherMap.
*   **Assamese Localization:** Full UI support for the Assamese language, ensuring accessibility for local farmers.

### 📋 Actionable Insights
*   **Fertilizer Prescription:** Calculates exact nutrient deficits (N, P, K) and recommends Urea, DAP, and MOP dosages per hectare.
*   **Economic Forecast:** Estimates market price, yield per hectare, gross revenue, and Net Profit (ROI) based on current Assam Mandi averages.
*   **PDF Export:** Generates professional, printable reports for offline use or government subsidy applications.
*   **Interactive Dashboard:** Visualizes environmental data through gauges, radar charts, and waterfall economic models.

### 📷 Computer Vision (Experimental)
*   **Crop Identification:** Utilizes Google Gemini AI to identify crops and detect visible diseases from photos taken directly in the field.

---

## 🛠️ Technology Stack
*   **Frontend:** [Streamlit](https://streamlit.io) (Interactive Web UI)
*   **Backend:** [Python 3.10+](https://python.org)
*   **ML Engine:** [Scikit-learn](https://scikit-learn.org) (Random Forest Classifier)
*   **Visualization:** [Plotly](https://plotly.com) (Dynamic charts)
*   **Data API:** [OpenWeatherMap](https://openweathermap.org/api)
*   **Computer Vision:** [Google Gemini API](https://ai.google.dev/)
*   **Reporting:** [fpdf2](https://github.com/fpdf2/fpdf2)

---

## ⚙️ System Architecture
1.  **Data Ingestion:** User inputs location and soil parameters.
2.  **Environmental Enrichment:** System fetches live district-level weather via REST API.
3.  **Vectorization:** Inputs are transformed into a 7-dimensional feature vector.
4.  **Inference:** The Random Forest model processes the vector against 50+ Assam-specific crop labels.
5.  **Post-Processing:** Calculations for fertilizer needs and economic profitability are performed.
6.  **Visualization:** Resulting data is rendered into localized UI components and PDF summaries.

---

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.10 or higher
*   OpenWeatherMap API Key
*   Google Gemini API Key (Optional, for camera features)

### Local Setup
1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/Crop_Recommendation_system.git
    cd Crop_Recommendation_system
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file or Streamlit `secrets.toml`:
    ```ini
    WEATHER_API_KEY=your_openweathermap_key
    GEMINI_API_KEY=your_google_ai_key
    ```

5.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure
```text
├── app.py                # Main Streamlit application logic
├── weather.py            # API integration for weather fetching
├── mappings.py           # Soil properties and seasonal rainfall data
├── model/                # Trained ML models and encoders
├── data/                 # Dataset used for training
├── notebooks/            # EDA and Model Training scripts
└── requirements.txt      # Project dependencies
```

---

## 🗺️ Roadmap
- [x] Multilingual Support (English/Assamese)
- [x] Fertilizer Prescription Engine
- [x] Real-time Weather Integration
- [x] Economic Profitability Forecast
- [ ] Mobile App version (Flutter/Kotlin)
- [ ] Satellite imagery integration for field health monitoring
- [ ] Community Forum for farmers to share best practices

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
**Disclaimer:** *This is a prototype system. Farmers are encouraged to consult with local agricultural extension officers before making significant financial or planting decisions.*
