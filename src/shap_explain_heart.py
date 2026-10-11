import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt

model = joblib.load("models/heart_model.pkl")
df = pd.read_csv("data/processed/heart_clean.csv")

X = df.drop(columns=["Target"])

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

patient_idx = 0
print("Patient data:\n", X.iloc[patient_idx])
print("\nActual outcome:", df["Target"].iloc[patient_idx])
print("Model prediction:", model.predict(X.iloc[[patient_idx]])[0])

print("\nSHAP contribution per feature (positive = pushes toward heart disease):")
for feature, value in zip(X.columns, shap_values[patient_idx]):
    print(f"  {feature}: {value:.4f}")

shap.summary_plot(shap_values, X, show=False)
plt.tight_layout()
plt.savefig("models/heart_shap_summary.png", dpi=150)
print("\nSummary plot saved to models/heart_shap_summary.png")