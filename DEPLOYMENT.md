# Deployment Instructions: Assam Crop Advisor

Congratulations! Your app is ready for the world. We will use **Streamlit Cloud** because it's free, reliable, and integrates directly with your code.

## 🛠️ Phase 1: Preparation (Done)
I have already updated your `requirements.txt`. I removed the heavy libraries like `torch` and `timm` (since we switched to Gemini AI) to ensure your cloud app starts in seconds rather than minutes.

## 📦 Phase 2: GitHub Upload
1.  **Commit your changes:** Ensure all your current code is pushed to a **Public** GitHub repository.
2.  **Verify .gitignore:** Make sure your `.env` and `data/history.db` are **NOT** on GitHub. We will handle secrets and data differently in the cloud.

## 🚀 Phase 3: Launch on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2.  Click **"Create app"** -> **"Yep, I have an app"**.
3.  Select your repository, the `main` branch, and set the Main file path to `app.py`.
4.  **CRITICAL STEP (Secrets):** 
    - Click **"Advanced settings..."** before deploying.
    - In the "Secrets" box, paste your API key like this:
      ```toml
      GEMINI_API_KEY = "your_api_key_here"
      ```
    - This replaces your local `.env` file safely in the cloud.

## 🌍 Phase 4: Share Your URL
Once the "Oven" finishes baking (deploying), you will get a URL like `https://assam-crop-advisor.streamlit.app`. You can send this to anyone!

---
**Mentor's Note:** In professional engineering, we call this **CI/CD (Continuous Integration / Continuous Deployment)**. Every time you push a change to GitHub, your website will automatically update!
