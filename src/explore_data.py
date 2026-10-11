import pandas as pd
import os

DATA_DIR = "data/raw"

def explore_dataset(filename):
    path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(path)
    print(f"\n===== {filename} =====")
    print("Shape:", df.shape)
    print("\nColumns:", list(df.columns))
    print("\nMissing values:\n", df.isnull().sum())
    print("\nFirst 5 rows:\n", df.head())
    return df

if __name__ == "__main__":
    datasets = ["diabetes.csv", "heart.csv", "liver.csv"]
    
    for file in datasets:
        try:
            explore_dataset(file)
        except FileNotFoundError:
            print(f"\n⚠️ {file} not found in {DATA_DIR}/ — download it first.")