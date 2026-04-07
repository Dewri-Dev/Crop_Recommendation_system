# Crop_Recommendation_system
# 🌱 AI-Based Crop Recommendation System for Assam 🌦️

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange)
![API](https://img.shields.io/badge/API-OpenWeatherMap-green)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

## 📌 Overview
Agriculture is the backbone of Assam's economy, but unpredictable weather patterns and a lack of scientific crop selection methods frequently lead to suboptimal yields. Existing agricultural software often requires complex technical inputs (like exact NPK values or soil pH) that are inaccessible to rural farmers.

This project is an **AI-driven, highly accessible web application** designed specifically for the climatic and soil conditions of Assam. By combining simple, intuitive user inputs with **real-time weather data**, our Machine Learning model predicts the most viable crop for cultivation, empowering farmers to make data-driven decisions without needing technical expertise.

---

## ✨ Key Features
* **Zero Technical Jargon:** Farmers only input basic parameters (e.g., district, general soil type, current season) instead of complex chemical values.
* **Real-Time Weather Integration:** Fetches live temperature, humidity, and rainfall data via the OpenWeatherMap API to ensure dynamic, up-to-date recommendations.
* **Region-Specific AI:** Trained on datasets tailored to the agricultural landscape of Assam (including crops like Tea, Rice, Mustard, and Jute).
* **Accessible UI:** A simple, icon-driven user interface with multilingual support (Assamese/Hindi).

---

## 🛠️ Technology Stack
* **Programming Language:** Python 3.x
* **Machine Learning:** Scikit-learn, Pandas, NumPy
* **Algorithms:** Random Forest Classifier / Decision Trees
* **Real-Time Data:** OpenWeatherMap API
* **Web Framework (UI):** Streamlit / Flask
* **Data Visualization:** Matplotlib / Seaborn (for data analysis)

---

## ⚙️ System Architecture
The recommendation pipeline follows a streamlined, 5-step data flow:
1. **User Input:** User selects basic parameters via the web UI.
2. **Data Preprocessing:** Categorical inputs are mapped to baseline numeric values typical for the specified region.
3. **API Call:** The system fetches live environmental data (temperature, humidity, precipitation).
4. **Feature Compilation:** User data and live weather data are combined into a single feature vector.
5. **ML Prediction:** The trained classification model processes the vector and outputs the top recommended crop.

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.8 or higher installed on your machine. You will also need a free API key from [OpenWeatherMap](https://openweathermap.org/api).

### Installation
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/assam-crop-recommendation.git](https://github.com/your-username/assam-crop-recommendation.git)
   cd assam-crop-recommendation
