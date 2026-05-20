import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


# [SYLLABUS MODULE 2]: DATA COLLECTION & DATA PRE-PROCESSING
# This section implements data loading and preparation techniques.
print("Loading dataset...")
df = pd.read_csv("data/Crop_recommendation.csv")

# Feature Selection
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = df['label']

# [SYLLABUS MODULE 2]: DATA TRANSFORMATION (LABEL ENCODING)
# Converting categorical text labels into numerical format for the ML model.
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# [SYLLABUS MODULE 4]: STATISTICAL FOUNDATIONS (DATA SPLITTING)
# Implementing the Train-Test Split (80/20) for model validation.
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# [SYLLABUS MODULE 5]: INTRODUCTION TO MACHINE LEARNING (MODEL TRAINING)
# Selecting and training the Random Forest Classifier algorithm.
print("Training the Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# [SYLLABUS MODULE 5]: MODEL EVALUATION
# Calculating accuracy to measure performance.
accuracy = model.score(X_test, y_test)
print(f"Model Training Complete! Accuracy: {accuracy * 100:.2f}%")

# [MODEL SERIALIZATION]
pickle.dump(model, open("model/crop_model.pkl", "wb"))
pickle.dump(le, open("model/label_encoder.pkl", "wb"))

print("Files saved: model/crop_model.pkl and model/label_encoder.pkl")
