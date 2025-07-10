import pandas as pd

# Load the dataset
dataset_path = 'static/data/diabetes.csv'
df = pd.read_csv(dataset_path)

# Display basic information
print("Dataset Info:")
print(df.info())
print("\nFirst 5 rows:")
print(df.head())
print("\nSummary statistics:")
print(df.describe())
print("\nMissing values:")
print(df.isnull().sum())