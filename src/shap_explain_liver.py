import pandas as pd
import numpy as np
import shap
import joblib
import matplotlib.pyplot as plt

model = joblib.load("models/liver_model.pkl")
df = pd.read_csv("data/processed/liver_clean.csv")

# Must match the log-transform applied during liver training
skewed_cols = [
    "Total_Bilirubin", "Direct_Bilirubin", "Alkaline_Phosphotase",
    "Alamine_Aminotransferase", "Aspartate_Aminotransferase"
]
for col in skewed_cols:
    df[col] = np.log1p(df[col])

X = df.drop(columns=["Target"])

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

patient_idx = 0
print("Patient data:\n", X.iloc[patient_idx])
print("\nActual outcome:", df["Target"].iloc[patient_idx])
print("Model prediction:", model.predict(X.iloc[[patient_idx]])[0])

print("\nSHAP contribution per feature (positive = pushes toward liver disease):")
for feature, value in zip(X.columns, shap_values[patient_idx]):
    print(f"  {feature}: {value:.4f}")

shap.summary_plot(shap_values, X, show=False)
plt.tight_layout()
plt.savefig("models/liver_shap_summary.png", dpi=150)
print("\nSummary plot saved to models/liver_shap_summary.png")