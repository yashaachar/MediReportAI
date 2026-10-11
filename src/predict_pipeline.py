import json
import os
import joblib
import numpy as np
import pandas as pd
import shap

from ocr_extract_pdf import pdf_to_images, ocr_image
from nlp_extract import extract_test_results, extract_patient_info
from feature_mapping import (
    build_feature_dict,
    DIABETES_MAP, DIABETES_DEFAULTS,
    HEART_MAP, HEART_DEFAULTS,
    LIVER_MAP, LIVER_DEFAULTS,
)

_BASE_DIR = os.path.join(os.path.dirname(__file__), "..")

def _model_path(name):
    return os.path.join(_BASE_DIR, "models", name)

DIABETES_FEATURES = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                      "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
HEART_FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
                   "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
LIVER_FEATURES = ["Age", "Gender", "Total_Bilirubin", "Direct_Bilirubin",
                   "Alkaline_Phosphotase", "Alamine_Aminotransferase",
                   "Aspartate_Aminotransferase", "Total_Protiens", "Albumin",
                   "Albumin_and_Globulin_Ratio"]

LIVER_LOG_COLS = [
    "Total_Bilirubin", "Direct_Bilirubin", "Alkaline_Phosphotase",
    "Alamine_Aminotransferase", "Aspartate_Aminotransferase"
]


def get_risk_color(probability, real_feature_ratio):
    """Combines model probability with data confidence to assign a risk color."""
    if probability < 0.35:
        base_tier = "GREEN"
    elif probability < 0.65:
        base_tier = "YELLOW"
    else:
        base_tier = "RED"

    low_confidence = real_feature_ratio < 0.4

    return {"color": base_tier, "low_confidence": low_confidence}


def run_full_pipeline(pdf_path):
    print(f"Processing: {pdf_path}")

    print("Running OCR...")
    pages = pdf_to_images(pdf_path)
    full_text = ""
    for page in pages:
        full_text += ocr_image(page) + "\n"

    print("Extracting test values...")
    tests = extract_test_results(full_text)
    patient_info = extract_patient_info(full_text)

    predictions = {}

    model_configs = [
        ("Diabetes", _model_path("diabetes_model.pkl"), DIABETES_MAP, DIABETES_DEFAULTS, DIABETES_FEATURES, False),
        ("Heart Disease", _model_path("heart_model.pkl"), HEART_MAP, HEART_DEFAULTS, HEART_FEATURES, False),
        ("Liver Disease", _model_path("liver_model.pkl"), LIVER_MAP, LIVER_DEFAULTS, LIVER_FEATURES, True),
    ]

    for disease_name, model_path, mapping, defaults, features, apply_log in model_configs:
        model = joblib.load(model_path)
        feat_dict, real_feats, default_feats = build_feature_dict(
            tests, patient_info, mapping, defaults, features
        )

        X = pd.DataFrame([feat_dict])[features]

        if apply_log:
            X_model_input = X.copy()
            for col in LIVER_LOG_COLS:
                X_model_input[col] = np.log1p(X_model_input[col])
        else:
            X_model_input = X

        pred = model.predict(X_model_input)[0]
        proba = model.predict_proba(X_model_input)[0][1]

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_model_input)
        # shap_values can be a list (for classifiers) or a 2D array
        if isinstance(shap_values, list):
            sv = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        else:
            sv = shap_values
        # sv shape: (1, n_features) → flatten to (n_features,)
        sv_row = sv[0] if hasattr(sv[0], '__len__') else sv
        top_features = sorted(
            zip(features, sv_row), key=lambda x: abs(x[1]), reverse=True
        )[:3]

        real_feature_ratio = len(real_feats) / len(features)
        risk = get_risk_color(proba, real_feature_ratio)

        predictions[disease_name] = {
            "prediction": int(pred),
            "probability": round(float(proba), 3),
            "risk_color": risk["color"],
            "low_confidence": risk["low_confidence"],
            "features_used": feat_dict,
            "real_data_features": real_feats,
            "default_features": default_feats,
            "top_shap_drivers": [(f, round(float(v), 4)) for f, v in top_features],
        }

    return {
        "patient_info": patient_info,
        "extracted_tests": tests,
        "predictions": predictions,
    }

if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_report.pdf"

    result = run_full_pipeline(pdf_path)

    print("\n" + "=" * 50)
    print("PATIENT INFO:", result["patient_info"])
    print("=" * 50)

    for disease, info in result["predictions"].items():
        status = "POSITIVE" if info["prediction"] == 1 else "NEGATIVE"
        color = info["risk_color"]
        conf_note = " (LOW CONFIDENCE - limited real data)" if info["low_confidence"] else ""
        print(f"\n{disease}: {status} — {color}{conf_note} (probability: {info['probability']})")
        print(f"  Real data used: {info['real_data_features']}")
        print(f"  Top factors: {info['top_shap_drivers']}")

    os.makedirs("data/pipeline_output", exist_ok=True)
    with open("data/pipeline_output/full_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n✅ Full result saved to data/pipeline_output/full_result.json")