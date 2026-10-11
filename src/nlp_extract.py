import re
import json
import os

KNOWN_TESTS = [
    "Hemoglobin", "RBC Count", "Hematocrit", "MCV", "MCH", "MCHC", "RDW CV",
    "WBC Count", "Platelet Count", "MPV",
    "Cholesterol", "Triglyceride", "HDL Cholesterol", "Direct LDL", "VLDL",
    "Fasting Blood Sugar", "HbA1c", "Mean Blood Glucose",
    "T3", "T4", "TSH",
    "Total Protein", "Albumin", "Globulin", "A/G Ratio",
    "Total Bilirubin", "Conjugated Bilirubin", "Unconjugated Bilirubin",
    "Iron", "Total Iron Binding Capacity", "Transferrin Saturation",
    "Creatinine", "Urea", "Blood Urea Nitrogen", "Uric Acid", "Calcium",
    "SGPT", "SGOT",
    "Sodium", "Potassium", "Chloride",
    "Vitamin B12", "25(OH) Vitamin D",
    "Direct LDL", "VLDL", "CHOL/HDL Ratio", "LDL/HDL Ratio",
]

KNOWN_TESTS_SORTED = sorted(KNOWN_TESTS, key=len, reverse=True)

# Maps alternate phrasings from other labs -> the canonical test name above
TEST_SYNONYMS = {
    "Glucose (Fasting)": "Fasting Blood Sugar",
    "Fasting Glucose": "Fasting Blood Sugar",
    "Blood Sugar Fasting": "Fasting Blood Sugar",
    "FBS": "Fasting Blood Sugar",
    "Random Blood Sugar": "Fasting Blood Sugar",
    "PP Blood Sugar": "Fasting Blood Sugar",
    "Blood Glucose After 2 hr": "Mean Blood Glucose",
    "Total Cholesterol": "Cholesterol",
    "Serum Cholesterol": "Cholesterol",
    "Triglycerides": "Triglyceride",
    "S. Creatinine": "Creatinine",
    "Serum Creatinine": "Creatinine",
    "SGOT/AST": "SGOT",
    "AST": "SGOT",
    "SGPT/ALT": "SGPT",
    "ALT": "SGPT",
    "Haemoglobin": "Hemoglobin",
    "Hb": "Hemoglobin",
    "WBC": "WBC Count",
    "Total WBC Count": "WBC Count",
    "RBC": "RBC Count",
    "Platelets": "Platelet Count",
    "PCV": "Hematocrit",
    "Vitamin D": "25(OH) Vitamin D",
    "Vitamin D3": "25(OH) Vitamin D",
    "Vitamin B-12": "Vitamin B12",
    "T.Bilirubin": "Total Bilirubin",
    "S. Sodium": "Sodium",
    "S. Potassium": "Potassium",
    "S. Chloride": "Chloride",
    "S. Calcium": "Calcium",
    "S. Uric Acid": "Uric Acid",
    "S. Albumin": "Albumin",
    "S. Total Protein": "Total Protein",
    "Total Iron Binding Capacity (TIBC)": "Total Iron Binding Capacity",
}

# Combined search list: real names + all synonym phrasings, longest first
ALL_SEARCHABLE_TERMS = KNOWN_TESTS + list(TEST_SYNONYMS.keys())
ALL_SEARCHABLE_TERMS_SORTED = sorted(ALL_SEARCHABLE_TERMS, key=len, reverse=True)

UNIT_WHITELIST = (
    r"g/dL|mg/dL|mg/mL|mmol/L|U/L|ng/mL|pg/mL|fL|pg|microlU/mL|mIU/mL|IU/mL|"
    r"mg/L|mg/g|S/Co|million/cmm|/cmm|micro\s?g/dL|%"
)

VALUE_UNIT_PATTERN = re.compile(
    r'(?:[HL]\s+)?(\d+\.?\d*)\s*(' + UNIT_WHITELIST + r')(?![a-zA-Z])',
    re.IGNORECASE
)


def is_likely_table_row(line):
    return len(line.split()) <= 15


def find_term(term, line):
    """Locate a search term in a line without relying on \\b, which fails
    when the term starts/ends in a non-word character like ')' or '%'."""
    pattern = r'(?<![A-Za-z0-9])' + re.escape(term) + r'(?![A-Za-z0-9])'
    return re.search(pattern, line, re.IGNORECASE)


def extract_test_results(text):
    results = {}
    lines = [l for l in text.split("\n") if is_likely_table_row(l)]

    for i, line in enumerate(lines):
        line_consumed = False
        for search_term in ALL_SEARCHABLE_TERMS_SORTED:
            test_name = TEST_SYNONYMS.get(search_term, search_term)

            if test_name in results or line_consumed:
                continue

            m = find_term(search_term, line)
            if not m:
                continue

            idx = m.start()
            same_line_rest = line[idx + len(search_term):]
            match = VALUE_UNIT_PATTERN.search(same_line_rest)

            if not match and i + 1 < len(lines):
                next_line = lines[i + 1]
                steals_another_test = any(
                    find_term(t, next_line) for t in ALL_SEARCHABLE_TERMS
                )
                if not steals_another_test:
                    match = VALUE_UNIT_PATTERN.search(next_line)

            if match:
                value, unit = match.groups()
                results[test_name] = {
                    "test": test_name,
                    "value": float(value),
                    "unit": unit
                }
                line_consumed = True

    # Merge in columnar-layout results (e.g. Lipid Profile page)
    columnar = extract_columnar_section(text)
    for k, v in columnar.items():
        if k not in results:
            results[k] = v

    return list(results.values())


def extract_patient_info(text):
    info = {}

    # ── AGE EXTRACTION ──
    # Format 1: "Sex / Age : Male / 25 Y"  (combined)
    age_match = re.search(r'Sex\s*/\s*Age\s*:\s*(Male|Female)\s*/\s*(\d+)\s*Y', text, re.IGNORECASE)
    if age_match:
        gender_str, age_str = age_match.groups()
        info["Gender"] = 1 if gender_str.lower() == "male" else 0
        info["Age"] = int(age_str)

    # Format 2: "Age : 25 Years" or "Age : 25 Yrs" or "Age : 25" (separate field)
    if "Age" not in info:
        age_match2 = re.search(
            r'(?<!\w)Age\s*[-—:_]*\s*:?\s*(\d{1,3})\s*(?:Years?|Yrs?|Y\b)?',
            text, re.IGNORECASE
        )
        if age_match2:
            age_val = int(age_match2.group(1))
            if 0 < age_val <= 120:
                info["Age"] = age_val

    # ── GENDER EXTRACTION ──
    # Format 2: "Gender : Male" or "Sex : Female" (separate field)
    if "Gender" not in info:
        gender_match = re.search(
            r'(?:Gender|Sex)\s*[-—:_]*\s*:?\s*(Male|Female|M|F)\b',
            text, re.IGNORECASE
        )
        if gender_match:
            g = gender_match.group(1).strip().lower()
            info["Gender"] = 1 if g in ("male", "m") else 0

    # ── NAME EXTRACTION ──
    # Skip "Client Name" (the lab's name, not the patient's).
    # Handle honorifics like Mr., Mrs., Ms., Dr., Master etc.
    # Allow dots, periods, and multi-word names (up to 4 words).
    name_match = re.search(
        r'(?<!Client\s)(?<!client\s)(?:Patient\s*)?Name\s*[-—:_]*\s*:?\s*'
        r'(?:(?:Mr|Mrs|Ms|Dr|Master|Miss|Smt)\.?\s+)?'   # optional honorific
        r'([A-Za-z][A-Za-z.]+(?:\s+[A-Za-z][A-Za-z.]*){0,3})',
        text, re.IGNORECASE
    )
    if name_match:
        raw_name = name_match.group(1).strip()
        # Remove trailing noise words that are actually field labels
        noise_words = {"lab", "no", "ref", "by", "collected", "age", "gender",
                       "sex", "report", "status", "date", "dob", "phone", "mobile"}
        parts = raw_name.split()
        cleaned = []
        for p in parts:
            if p.lower().rstrip(".:") in noise_words:
                break
            cleaned.append(p)
        if cleaned:
            info["Name"] = " ".join(cleaned)

    return info


def extract_columnar_section(text):
    """Handle pages where test names and values sit in separate blocks
    (e.g. the Lipid Profile page), pairing them by position."""
    lines = text.split("\n")
    results = {}

    for i, line in enumerate(lines):
        if line.strip() == "Test":
            names = []
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("Result"):
                candidate = lines[j].strip()
                match = next((t for t in KNOWN_TESTS_SORTED if candidate.lower() == t.lower()), None)
                if match:
                    names.append(match)
                j += 1

            if not names:
                continue

            k = j
            values_found = []
            while k < len(lines) and len(values_found) < len(names):
                m = VALUE_UNIT_PATTERN.search(lines[k])
                if m:
                    values_found.append(m.groups())
                k += 1

            for test_name, (value, unit) in zip(names, values_found):
                if test_name not in results:
                    results[test_name] = {
                        "test": test_name,
                        "value": float(value),
                        "unit": unit
                    }

    return results


if __name__ == "__main__":
    input_path = "data/ocr_output/sample_extracted.txt"

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    results = extract_test_results(text)
    patient_info = extract_patient_info(text)

    print(f"Patient info: {patient_info}\n")
    print(f"Extracted {len(results)} unique test results:\n")
    for r in results:
        print(r)

    os.makedirs("data/nlp_output", exist_ok=True)

    output = {"patient_info": patient_info, "tests": results}
    with open("data/nlp_output/extracted_tests.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Saved to data/nlp_output/extracted_tests.json")