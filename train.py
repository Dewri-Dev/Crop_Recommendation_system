import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# 1. LOAD THE DATASET
# This CSV contains rows of soil data (N,P,K,pH) and weather (Temp, Humidity, Rain)
print("Loading dataset...")
df = pd.read_csv("data/Crop_recommendation.csv")

# 2. SEPARATE FEATURES AND TARGET
# X = Input variables (N, P, K, temperature, humidity, ph, rainfall)
# y = Output variable (label / crop name)
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = df['label']

# 3. ENCODE THE CROP NAMES
# Computers understand numbers better than text. 
# LabelEncoder converts 'rice' to 0, 'maize' to 1, etc.
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 4. SPLIT DATA FOR TESTING
# We use 80% of data for training and 20% to test if the AI learned correctly.
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# 5. TRAIN THE MODEL (THE "BRAIN")
# Random Forest is like a group of decision trees voting on the best crop.
print("Training the Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. EVALUATE
accuracy = model.score(X_test, y_test)
print(f"Model Training Complete! Accuracy: {accuracy * 100:.2f}%")

# 7. SAVE THE BRAIN TO DISK
# We save these files so our app.py can use them later without re-training.
pickle.dump(model, open("model/crop_model.pkl", "wb"))
pickle.dump(le, open("model/label_encoder.pkl", "wb"))

print("Files saved: model/crop_model.pkl and model/label_encoder.pkl")
