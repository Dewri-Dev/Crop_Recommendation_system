# 🌱 Assam Crop Advisor: Hybrid AI System

An intelligent, regionally-tailored crop recommendation system for Assam, India. This project fuses traditional **Machine Learning** with modern **Generative AI** to provide both predictive accuracy and expert human-like guidance.

---

## 🚀 Key Features

*   **Hybrid AI Architecture**: 
    *   **Predictive Phase**: Uses a **Random Forest Classifier** trained on a custom 4,900-record dataset covering 49 Assam-specific crops (including Joha Rice, Bhut Jolokia, and Assam Tea).
    *   **Prescriptive Phase**: Integrates **Groq AI (Llama 3.3)** to generate context-aware farming tips based on live environmental conditions.
*   **Real-Time Data Bridge**: Automatically fetches live temperature and humidity for Assam districts via the **OpenWeatherMap REST API**.
*   **Zero-Friction UI**: Deployed using **Gradio**, providing an instant mobile-friendly web interface and a secure public sharing link.
*   **Visual Context**: Automatically retrieves real photographs of recommended crops using the **Wikipedia API**.

---

## 🛠️ Technology Stack

| Domain | Tool / Library |
| :--- | :--- |
| **Language** | Python 3.10 |
| **ML Framework** | Scikit-Learn |
| **Generative AI** | Groq (Llama 3.3-70b) |
| **Web UI** | Gradio |
| **Weather Data** | OpenWeatherMap API |
| **Visualization** | Seaborn, Matplotlib |
| **DevOps** | python-dotenv (Secrets Management) |

---

## 📂 Project Structure

```text
├── app.py                # Main Gradio application (UI + Logic)
├── train.py              # Model training engine
├── weather.py            # API helper for OpenWeatherMap
├── data/                 # Extended 49-crop Assam dataset
├── model/                # Serialized .pkl files (Brain of the system)
├── microproject.txt      # Professional LaTeX Documentation (Overleaf)
└── requirements.txt      # Python dependencies
```

---

## 💻 Installation & Usage

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Dewri-Dev/Crop_Recommendation_system.git
cd Crop_Recommendation_system

# Install dependencies
pip install -r requirements.txt
```

### 3. API Configuration
Create a `.env` file in the root directory and add your keys:
```env
WEATHER_API_KEY=your_openweathermap_key
GROQ_API_KEY=your_groq_api_key
```

### 4. Run the App
```bash
python app.py
```

---

## 🏆 Unique Selling Points for Viva
1.  **Defeats Data Drift**: Unlike static models, this system is contextually aware of the current hour's weather.
2.  **High Cardinality**: Categorizes 49 classes instead of the standard 22, proving regional dataset augmentation.
3.  **Prescriptive Analytics**: Moves beyond "What to plant" to "How to plant" using Generative AI.

---
*Developed for the Micro Project component at Assam Science and Technology University (ASTU), 2026.*
