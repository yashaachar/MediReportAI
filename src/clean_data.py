import pandas as pd
import os

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

def clean_liver():
    df = pd.read_csv(os.path.join(RAW_DIR, "liver.csv"))
    
    # Fill missing Albumin_and_Globulin_Ratio with median
    df["Albumin_and_Globulin_Ratio"] = df["Albumin_and_Globulin_Ratio"].fillna(
        df["Albumin_and_Globulin_Ratio"].median()
    )
    
    # Encode Gender: Male=1, Female=0
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})
    
    # Dataset column: 1 = liver disease, 2 = no liver disease -> convert to 1/0
    df["Dataset"] = df["Dataset"].map({1: 1, 2: 0})
    df = df.rename(columns={"Dataset": "Target"})
    
    df.to_csv(os.path.join(PROCESSED_DIR, "liver_clean.csv"), index=False)
    print("liver_clean.csv saved. Shape:", df.shape)
    print(df["Target"].value_counts())
    return df

def clean_diabetes():
    df = pd.read_csv(os.path.join(RAW_DIR, "diabetes.csv"))
    df = df.rename(columns={"Outcome": "Target"})
    df.to_csv(os.path.join(PROCESSED_DIR, "diabetes_clean.csv"), index=False)
    print("\ndiabetes_clean.csv saved. Shape:", df.shape)
    print(df["Target"].value_counts())
    return df

def clean_heart():
    df = pd.read_csv(os.path.join(RAW_DIR, "heart.csv"))
    df = df.rename(columns={"condition": "Target"})
    df.to_csv(os.path.join(PROCESSED_DIR, "heart_clean.csv"), index=False)
    print("\nheart_clean.csv saved. Shape:", df.shape)
    print(df["Target"].value_counts())
    return df

if __name__ == "__main__":
    clean_liver()
    clean_diabetes()
    clean_heart()