import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load the dataset
dataset_path = 'static/data/diabetes.csv'
df = pd.read_csv(dataset_path)

# Preprocess the dataset
columns_with_invalid_zeros = ['Glucose', 'BMI']
df[columns_with_invalid_zeros] = df[columns_with_invalid_zeros].replace(0, np.nan)
df.fillna(df.median(), inplace=True)

# Select features (Age, Glucose, BMI)
features = ['Glucose', 'Age', 'BMI']
X = df[features]
y = df['Outcome']  # 0: Non-diabetic, 1: Diabetic

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate the model
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save the model and scaler
joblib.dump(model, 'static/model/diabetes_model.pkl')
joblib.dump(scaler, 'static/model/scaler.pkl')
print("Model and scaler saved to static/model/")
