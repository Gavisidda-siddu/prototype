import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import numpy as np

class HeartDiseaseModel:
    def __init__(self):
        self.model = None
        self.features = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 
                        'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 
                        'Oldpeak', 'ST_Slope']
        self.target = 'HeartDisease'
        
    def load_data(self, filepath):
        """Load and preprocess the heart data"""
        data = pd.read_csv(filepath)
        
        # Convert categorical variables
        data['Sex'] = data['Sex'].map({'M': 1, 'F': 0})
        data['ExerciseAngina'] = data['ExerciseAngina'].map({'Y': 1, 'N': 0})
        data['ChestPainType'] = data['ChestPainType'].map({
            'ATA': 0, 'NAP': 1, 'ASY': 2, 'TA': 3
        })
        data['RestingECG'] = data['RestingECG'].map({
            'Normal': 0, 'ST': 1, 'LVH': 2
        })
        data['ST_Slope'] = data['ST_Slope'].map({
            'Up': 0, 'Flat': 1, 'Down': 2
        })
        
        return data

    def train_model(self, data_path='static/data/heart_recommendations_indian.csv'):
        """Train the Random Forest model"""
        data = self.load_data(data_path)
        X = data[self.features]
        y = data[self.target]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy:.2f}")
        
        # Save the model
        joblib.dump(self.model, 'heart_model.pkl')
        
    def predict_risk(self, input_data):
        """Predict heart disease risk for given input"""
        if not self.model:
            self.model = joblib.load('heart_model.pkl')
            
        # Convert input data to DataFrame
        input_df = pd.DataFrame([input_data], columns=self.features)
        
        # Make prediction
        prediction = self.model.predict(input_df)
        probability = self.model.predict_proba(input_df)
        
        return {
            'prediction': int(prediction[0]),
            'probability': float(probability[0][1]),
            'risk_level': 'High' if prediction[0] == 1 else 'Low'
        }

# Example usage
if __name__ == "__main__":
    model = HeartDiseaseModel()
    model.train_model()
    
    # Test prediction
    test_data = {
        'Age': 50, 'Sex': 1, 'ChestPainType': 2, 'RestingBP': 140,
        'Cholesterol': 289, 'FastingBS': 0, 'RestingECG': 0,
        'MaxHR': 172, 'ExerciseAngina': 0, 'Oldpeak': 0.0, 'ST_Slope': 0
    }
    print(model.predict_risk(test_data))