import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt

# Load model and data
model = joblib.load("models/diabetes_model.pkl")
df = pd.read_csv("data/processed/diabetes_clean.csv")

X = df.drop(columns=["Target"])

# Create SHAP explainer for tree-based models
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Pick one patient (row 0) to explain individually
patient_idx = 0
print("Patient data:\n", X.iloc[patient_idx])
print("\nActual outcome:", df["Target"].iloc[patient_idx])
print("Model prediction:", model.predict(X.iloc[[patient_idx]])[0])

# Print SHAP values for this patient — shows push toward/away from disease
print("\nSHAP contribution per feature (positive = pushes toward diabetes):")
for feature, value in zip(X.columns, shap_values[patient_idx]):
    print(f"  {feature}: {value:.4f}")

# Save a summary plot (overall feature importance across all patients)
shap.summary_plot(shap_values, X, show=False)
plt.tight_layout()
plt.savefig("models/diabetes_shap_summary.png", dpi=150)
print("\nSummary plot saved to models/diabetes_shap_summary.png")