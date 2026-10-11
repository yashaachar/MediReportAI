import json

DIABETES_MAP = {
    "Fasting Blood Sugar": "Glucose",
}
HEART_MAP = {
    "Cholesterol": "chol",
}
LIVER_MAP = {
    "Total Bilirubin": "Total_Bilirubin",
    "Unconjugated Bilirubin": "Direct_Bilirubin",  # closest available proxy
    "SGPT": "Alamine_Aminotransferase",
    "SGOT": "Aspartate_Aminotransferase",
    "Total Protein": "Total_Protiens",
    "Albumin": "Albumin",
}

DIABETES_DEFAULTS = {
    "Pregnancies": 0, "BloodPressure": 72, "SkinThickness": 20,
    "Insulin": 80, "BMI": 25.0, "DiabetesPedigreeFunction": 0.4
}
HEART_DEFAULTS = {
    "sex": 1, "cp": 0, "trestbps": 120, "fbs": 0, "restecg": 0,
    "thalach": 150, "exang": 0, "oldpeak": 0.0, "slope": 1, "ca": 0, "thal": 2
}
LIVER_DEFAULTS = {
    "Alkaline_Phosphotase": 100, "Albumin_and_Globulin_Ratio": 1.0
}


def build_feature_dict(extracted_tests, patient_info, mapping, defaults, all_features):
    lookup = {t["test"]: t["value"] for t in extracted_tests}

    feature_dict = {}
    used_real_data = []
    used_defaults = []

    for feature in all_features:
        # Age/Gender come from patient_info, not the test table
        if feature.lower() == "age" and "Age" in patient_info:
            feature_dict[feature] = patient_info["Age"]
            used_real_data.append(feature)
            continue
        if feature.lower() in ("sex", "gender") and "Gender" in patient_info:
            feature_dict[feature] = patient_info["Gender"]
            used_real_data.append(feature)
            continue

        source_test = next((k for k, v in mapping.items() if v == feature), None)

        if source_test and source_test in lookup:
            feature_dict[feature] = lookup[source_test]
            used_real_data.append(feature)
        elif feature in defaults:
            feature_dict[feature] = defaults[feature]
            used_defaults.append(feature)
        else:
            feature_dict[feature] = 0
            used_defaults.append(feature)

    return feature_dict, used_real_data, used_defaults


if __name__ == "__main__":
    with open("data/nlp_output/extracted_tests.json", "r") as f:
        data = json.load(f)

    extracted = data["tests"]
    patient_info = data["patient_info"]

    DIABETES_FEATURES = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                          "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
    HEART_FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
                       "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
    LIVER_FEATURES = ["Age", "Gender", "Total_Bilirubin", "Direct_Bilirubin",
                       "Alkaline_Phosphotase", "Alamine_Aminotransferase",
                       "Aspartate_Aminotransferase", "Total_Protiens", "Albumin",
                       "Albumin_and_Globulin_Ratio"]

    for name, mapping, defaults, feats in [
        ("DIABETES", DIABETES_MAP, DIABETES_DEFAULTS, DIABETES_FEATURES),
        ("HEART", HEART_MAP, HEART_DEFAULTS, HEART_FEATURES),
        ("LIVER", LIVER_MAP, LIVER_DEFAULTS, LIVER_FEATURES),
    ]:
        fd, real, defaulted = build_feature_dict(extracted, patient_info, mapping, defaults, feats)
        print(f"\n===== {name} MODEL INPUT =====")
        print("Features:", fd)
        print(f"From real report data: {real}")
        print(f"Using defaults: {defaulted}")