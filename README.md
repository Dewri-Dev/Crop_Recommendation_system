# 🌾 Assam Crop Advisor 

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered decision support system designed specifically for farmers in Assam, India. This application combines Machine Learning, Live Weather Data, and **AI Vision** to provide hyper-local crop recommendations, fertilizer prescriptions, and market forecasts.

## 🚀 Key Features

- **🤖 Random Forest ML Engine:** Predicts the best-suited crop based on NPK, pH, and historical climate data.
- **📸 AI Vision Identification:** Identify crops using **Groq Cloud AI (Llama 4 Vision)** with a robust offline MobileNetV3 fallback.
- **🌦️ Live Weather Integration:** Automatically fetches real-time temperature and humidity based on the selected Assam district.
- **🇮🇳 Bilingual Support:** Full interface support for both **English** and **অসমীয়া (Assamese)**.
- **🧪 Fertilizer Engine:** Provides exact dosage recommendations (Urea, DAP, MOP) based on soil nutrient deficits.
- **💰 Market Forecaster:** Estimates gross revenue, input costs, and Net Profit (ROI) using current Assam Mandi averages.
- **📄 PDF Reports:** Generate and download professional field reports for offline reference.
- **📂 Persistent History:** Securely saves all recommendation reports to a local **SQLite** database.

## 🏗️ Project Architecture

The project follows a modular, clean-code architecture for maintainability:

- `app.py`: Main Streamlit frontend and orchestration.
- `config/`: Externalized Data & Translations (JSON).
- `logic/`: Business Calculation Engines (Fertilizer, Market, PDF).
- `services/`: External API integrations (Groq, Weather, Wikipedia).
- `utils/`: Shared Utilities (Logger, Database).
- `model/`: Trained ML Models & AI Labels.
- `tests/`: Automated Logic Tests.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dewri-Dev/Crop_Recommendation_system.git
   cd Crop_Recommendation_system
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key
   WEATHER_API_KEY=your_openweathermap_key
   ```

5. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## 🧪 Testing

To ensure the calculation engines are working correctly, run the automated test suite:
```bash
pytest
```

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---
**Built with ❤️ for the farmers of Assam.**
