from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from deep_translator import GoogleTranslator
import json
import os
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "fonts", "NotoSansDevanagari-Regular.ttf")
pdfmetrics.registerFont(TTFont("NotoDevanagari", FONT_PATH))
pdfmetrics.registerFontFamily(
    "NotoDevanagari",
    normal="NotoDevanagari",
    bold="NotoDevanagari",
    italic="NotoDevanagari",
    boldItalic="NotoDevanagari"
)

RISK_COLORS = {
    "GREEN": HexColor("#2e7d32"),
    "YELLOW": HexColor("#e65100"),
    "RED": HexColor("#c62828"),
}

RISK_BG = {
    "GREEN": HexColor("#e8f5e9"),
    "YELLOW": HexColor("#fff3e0"),
    "RED": HexColor("#ffebee"),
}

RISK_LABELS = {
    "GREEN": "Low Risk",
    "YELLOW": "Moderate Risk",
    "RED": "High Risk",
}

# ── Human-friendly feature name mapping ──
FEATURE_DISPLAY_NAMES = {
    "Glucose": "Blood Glucose",
    "BMI": "BMI (Body Mass Index)",
    "BloodPressure": "Blood Pressure",
    "SkinThickness": "Skin Thickness",
    "Insulin": "Insulin Level",
    "DiabetesPedigreeFunction": "Diabetes Family History Score",
    "Pregnancies": "Pregnancies",
    "Age": "Age",
    "age": "Age",
    "sex": "Sex",
    "cp": "Chest Pain Type",
    "trestbps": "Resting Blood Pressure",
    "chol": "Cholesterol",
    "fbs": "Fasting Blood Sugar",
    "restecg": "Resting ECG",
    "thalach": "Max Heart Rate",
    "exang": "Exercise Angina",
    "oldpeak": "ST Depression",
    "slope": "ST Slope",
    "ca": "Major Vessels (Fluoroscopy)",
    "thal": "Thalassemia",
    "Gender": "Gender",
    "Total_Bilirubin": "Total Bilirubin",
    "Direct_Bilirubin": "Direct Bilirubin",
    "Alkaline_Phosphotase": "Alkaline Phosphatase",
    "Alamine_Aminotransferase": "ALT (SGPT)",
    "Aspartate_Aminotransferase": "AST (SGOT)",
    "Total_Protiens": "Total Proteins",
    "Albumin": "Albumin",
    "Albumin_and_Globulin_Ratio": "A/G Ratio",
}

FEATURE_DISPLAY_NAMES_HI = {
    "Glucose": "रक्त शर्करा (Glucose)",
    "BMI": "बीएमआई (BMI)",
    "BloodPressure": "रक्तचाप (Blood Pressure)",
    "SkinThickness": "त्वचा की मोटाई (Skin Thickness)",
    "Insulin": "इंसुलिन स्तर (Insulin)",
    "DiabetesPedigreeFunction": "पारिवारिक इतिहास स्कोर (DPF)",
    "Pregnancies": "गर्भधारण संख्या (Pregnancies)",
    "Age": "आयु (Age)",
    "age": "आयु (Age)",
    "sex": "लिंग (Sex)",
    "cp": "सीने में दर्द का प्रकार (Chest Pain)",
    "trestbps": "विश्राम रक्तचाप (Resting BP)",
    "chol": "कोलेस्ट्रॉल (Cholesterol)",
    "fbs": "फास्टिंग ब्लड शुगर (FBS)",
    "restecg": "विश्राम ईसीजी (Resting ECG)",
    "thalach": "अधिकतम हृदय गति (Max Heart Rate)",
    "exang": "व्यायाम प्रेरित एनजाइना (Exercise Angina)",
    "oldpeak": "एसटी डिप्रेशन (ST Depression)",
    "slope": "एसटी ढलान (ST Slope)",
    "ca": "प्रमुख रक्त वाहिकाएं (Major Vessels)",
    "thal": "थैलेसीमिया (Thalassemia)",
    "Gender": "लिंग (Gender)",
    "Total_Bilirubin": "टोटल बिलीरुबिन (Total Bilirubin)",
    "Direct_Bilirubin": "डायरेक्ट बिलीरुबिन (Direct Bilirubin)",
    "Alkaline_Phosphotase": "एल्कलाइन फॉस्फेटेज (ALP)",
    "Alamine_Aminotransferase": "एएलटी / एसजीपीटी (ALT)",
    "Aspartate_Aminotransferase": "एएसटी / एसजीओटी (AST)",
    "Total_Protiens": "कुल प्रोटीन (Total Proteins)",
    "Albumin": "एल्बुमिन (Albumin)",
    "Albumin_and_Globulin_Ratio": "ए/जी अनुपात (A/G Ratio)",
}

STATIC_TRANSLATIONS_HI = {
    "MediReport AI": "मेडीरिपोर्ट एआई",
    "Health Analysis Summary": "स्वास्थ्य विश्लेषण सारांश",
    "Patient Information": "रोगी की जानकारी",
    "Patient Name": "रोगी का नाम",
    "Age": "आयु",
    "Gender": "लिंग",
    "Male": "पुरुष",
    "Female": "महिला",
    "Other": "अन्य",
    "N/A": "अनुपलब्ध",
    "Not specified": "निर्दिष्ट नहीं",
    "Diabetes": "मधुमेह (डायबिटीज)",
    "Heart Disease": "हृदय रोग",
    "Liver Disease": "यकृत (लिवर) रोग",
    "Positive": "सकारात्मक (Positive)",
    "Negative": "नकारात्मक (Negative)",
    "Low Risk": "कम जोखिम (Low Risk)",
    "Moderate Risk": "मध्यम जोखिम (Moderate Risk)",
    "High Risk": "उच्च जोखिम (High Risk)",
    "Unknown": "अज्ञात",
    "Risk Level": "जोखिम स्तर",
    "Probability": "संभावना",
    "Limited real report data used — default baseline values were applied. Result confidence is lower.": "सीमित वास्तविक रिपोर्ट डेटा मिला — डिफ़ॉल्ट आधारभूत मान लागू किए गए। परिणाम की विश्वसनीयता कम है।",
    "Data extracted from your report": "आपकी रिपोर्ट से निकाला गया डेटा",
    "Estimated / default values": "अनुमानित / डिफ़ॉल्ट आधारभूत मान",
    "Key Contributing Factors (SHAP)": "प्रमुख योगदान कारक (SHAP)",
    "Key Contributing Factors": "प्रमुख योगदान कारक",
    "Feature": "लक्षण / कारक",
    "Impact": "प्रभाव",
    "Direction": "दिशा",
    "Increases Risk": "जोखिम बढ़ाता है",
    "Decreases Risk": "जोखिम घटाता है",
    "↑ Increases Risk": "↑ जोखिम बढ़ाता है",
    "↓ Decreases Risk": "↓ जोखिम घटाता है",
    "Extracted Test Values": "निकाले गए लैब परीक्षण मान",
    "Test Name": "परीक्षण का नाम",
    "Value": "मान",
    "Unit": "इकाई",
    "Medical Disclaimer": "चिकित्सा अस्वीकरण",
    "This report is generated by MediReport AI for informational and screening purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for clinical decisions.": "यह रिपोर्ट केवल सूचनात्मक और स्क्रीनिंग उद्देश्यों के लिए मेडीरिपोर्ट एआई द्वारा तैयार की गई है। यह पेशेवर चिकित्सा सलाह, निदान या उपचार का विकल्प नहीं है। नैदानिक निर्णयों के लिए हमेशा किसी योग्य चिकित्सक या स्वास्थ्य सेवा प्रदाता से परामर्श लें।",
    "Generated by MediReport AI": "मेडीरिपोर्ट एआई द्वारा जनरेट किया गया",
}

_TRANSLATION_CACHE = {}

def translate_text(text, target_lang="hi"):
    if not text or not isinstance(text, str):
        return text
    clean_text = text.strip()
    clean_key = re.sub(r'^[⚠\s*•\-!]+', '', clean_text).strip()

    if target_lang == "hi":
        if clean_key in STATIC_TRANSLATIONS_HI:
            return STATIC_TRANSLATIONS_HI[clean_key]
        if clean_text in STATIC_TRANSLATIONS_HI:
            return STATIC_TRANSLATIONS_HI[clean_text]

    cache_key = (clean_key, target_lang)
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    try:
        translated = GoogleTranslator(source="en", target=target_lang).translate(clean_key)
        if translated:
            _TRANSLATION_CACHE[cache_key] = translated
            return translated
    except Exception as e:
        safe_msg = clean_key.encode("ascii", "replace").decode("ascii")
        print(f"[Translation fallback for '{safe_msg}']: {type(e).__name__}")

    return clean_text


def _get_display_name(feature_key, language="en"):
    """Return a human-readable name for a model feature."""
    if language == "hi":
        if feature_key in FEATURE_DISPLAY_NAMES_HI:
            return FEATURE_DISPLAY_NAMES_HI[feature_key]
        en_name = FEATURE_DISPLAY_NAMES.get(feature_key, feature_key)
        return FEATURE_DISPLAY_NAMES_HI.get(en_name, translate_text(en_name, "hi"))
    return FEATURE_DISPLAY_NAMES.get(feature_key, feature_key)


def generate_pdf_report(result, output_path, language="en"):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=20*mm, bottomMargin=20*mm,
        leftMargin=18*mm, rightMargin=18*mm
    )

    # ── Styles ──
    styles = getSampleStyleSheet()
    base_font = "NotoDevanagari" if language == "hi" else "Helvetica"
    bold_font = "NotoDevanagari" if language == "hi" else "Helvetica-Bold"

    if language == "hi":
        for style_name in ["Title", "Normal", "Italic", "Heading2"]:
            styles[style_name].fontName = "NotoDevanagari"

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontName=bold_font, fontSize=20, leading=26,
        textColor=HexColor("#1a1a2e"), alignment=TA_CENTER,
        spaceAfter=4*mm
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"],
        fontName=base_font, fontSize=9, leading=12,
        textColor=HexColor("#6b7280"), alignment=TA_CENTER,
        spaceAfter=6*mm
    )
    patient_style = ParagraphStyle(
        "PatientInfo", parent=styles["Normal"],
        fontName=base_font, fontSize=10.5, leading=16,
        textColor=HexColor("#374151"), spaceAfter=2*mm
    )
    section_header_style = ParagraphStyle(
        "SectionHeader", parent=styles["Heading2"],
        fontName=bold_font, fontSize=14, leading=20,
        spaceAfter=3*mm
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName=base_font, fontSize=9.5, leading=14,
        textColor=HexColor("#374151")
    )
    note_style = ParagraphStyle(
        "NoteText", parent=styles["Italic"],
        fontName=base_font, fontSize=8.5, leading=12,
        textColor=HexColor("#9ca3af"), spaceAfter=2*mm
    )
    small_style = ParagraphStyle(
        "SmallText", parent=styles["Normal"],
        fontName=base_font, fontSize=8, leading=11,
        textColor=HexColor("#9ca3af"), alignment=TA_CENTER
    )

    elements = []

    # ══════════════════════════════════════════
    #  HEADER
    # ══════════════════════════════════════════
    title_text = "MediReport AI"
    subtitle_text = "Health Analysis Summary"
    if language == "hi":
        title_text = translate_text(title_text)
        subtitle_text = translate_text(subtitle_text)

    elements.append(Paragraph(title_text, title_style))
    elements.append(Paragraph(subtitle_text, subtitle_style))

    # Gradient-style line
    elements.append(HRFlowable(
        width="100%", thickness=1.5,
        color=HexColor("#06b6d4"), spaceAfter=5*mm
    ))

    # ══════════════════════════════════════════
    #  PATIENT INFO BOX
    # ══════════════════════════════════════════
    patient = result.get("patient_info", {})
    name = patient.get("Name", "N/A")
    age = patient.get("Age", "N/A")
    gender_val = patient.get("Gender")
    if gender_val == 1:
        gender = "Male"
    elif gender_val == 0:
        gender = "Female"
    else:
        gender = "N/A"

    if language == "hi":
        gender = translate_text(gender)

    pat_name_label = "Patient Name" if language == "en" else translate_text("Patient Name")
    pat_age_label = "Age" if language == "en" else translate_text("Age")
    pat_gender_label = "Gender" if language == "en" else translate_text("Gender")

    # Build patient info as a clean table row
    pat_data = [
        [
            Paragraph(f'<b>{pat_name_label}:</b> {name}', patient_style),
            Paragraph(f'<b>{pat_age_label}:</b> {age}', patient_style),
            Paragraph(f'<b>{pat_gender_label}:</b> {gender}', patient_style),
        ]
    ]
    pat_table = Table(pat_data, colWidths=[75*mm, 45*mm, 45*mm])
    pat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.8, HexColor("#e2e8f0")),
        ("FONTNAME", (0, 0), (-1, -1), base_font),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(pat_table)
    elements.append(Spacer(1, 8*mm))

    # ══════════════════════════════════════════
    #  DISEASE PREDICTION CARDS
    # ══════════════════════════════════════════
    for disease, info in result["predictions"].items():
        disease_label = disease
        status_label = "Positive" if info["prediction"] == 1 else "Negative"
        risk_color_key = info.get("risk_color", "GREEN")
        color = RISK_COLORS.get(risk_color_key, HexColor("#000000"))
        bg = RISK_BG.get(risk_color_key, HexColor("#f5f5f5"))
        risk_label = RISK_LABELS.get(risk_color_key, "Unknown")

        if language == "hi":
            disease_label = translate_text(disease_label)
            status_label = translate_text(status_label)
            risk_label = translate_text(risk_label)

        card_elements = []

        # ── Disease header with colored background ──
        header_style = ParagraphStyle(
            f"DiseaseHeader_{disease}", parent=styles["Heading2"],
            textColor=color, fontName=bold_font, fontSize=13, leading=18,
            spaceBefore=0, spaceAfter=1*mm
        )
        card_elements.append(Paragraph(
            f"{disease_label}: {status_label}",
            header_style
        ))

        # Risk badge
        badge_style = ParagraphStyle(
            f"Badge_{disease}", parent=styles["Normal"],
            fontName=bold_font, fontSize=10, leading=14,
            textColor=color
        )
        prob_pct = info['probability'] * 100
        risk_lvl_lbl = "Risk Level" if language == "en" else translate_text("Risk Level")
        prob_lbl = "Probability" if language == "en" else translate_text("Probability")
        card_elements.append(Paragraph(
            f"{risk_lvl_lbl}: {risk_label}  •  {prob_lbl}: {prob_pct:.1f}%",
            badge_style
        ))
        card_elements.append(Spacer(1, 2*mm))

        # ── Confidence note ──
        if info.get("low_confidence"):
            if language == "hi":
                raw_note = translate_text("Limited real report data used — default baseline values were applied. Result confidence is lower.")
                conf_note = f"[!] {raw_note}"
            else:
                conf_note = "⚠ Limited real report data used — default baseline values were applied. Result confidence is lower."
            card_elements.append(Paragraph(conf_note, note_style))

        # ── Data source tags ──
        real_feats = info.get("real_data_features", [])
        default_feats = info.get("default_features", [])

        if real_feats:
            real_str = ", ".join(_get_display_name(f, language) for f in real_feats)
            label = "Data extracted from your report" if language == "en" else translate_text("Data extracted from your report")
            card_elements.append(Paragraph(
                f'<b>{label}:</b> {real_str}', body_style
            ))

        if default_feats:
            def_str = ", ".join(_get_display_name(f, language) for f in default_feats)
            label = "Estimated / default values" if language == "en" else translate_text("Estimated / default values")
            card_elements.append(Paragraph(
                f'<b>{label}:</b> {def_str}', body_style
            ))

        card_elements.append(Spacer(1, 2*mm))

        # ── SHAP factors table ──
        factors_label = "Key Contributing Factors (SHAP)" if language == "en" else translate_text("Key Contributing Factors")
        card_elements.append(Paragraph(f"<b>{factors_label}</b>", body_style))
        card_elements.append(Spacer(1, 1*mm))

        table_header = ["Feature", "Impact", "Direction"]
        if language == "hi":
            table_header = [translate_text(h) for h in table_header]

        table_data = [table_header]
        for feat, val in info["top_shap_drivers"]:
            if language == "hi":
                dir_label = translate_text("Increases Risk") if val > 0 else translate_text("Decreases Risk")
                direction = f"↑ {dir_label}" if val > 0 else f"↓ {dir_label}"
            else:
                direction = "↑ Increases Risk" if val > 0 else "↓ Decreases Risk"
            table_data.append([
                _get_display_name(feat, language),
                f"{abs(val):.4f}",
                direction
            ])

        table = Table(table_data, colWidths=[65*mm, 30*mm, 55*mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#334155")),
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        # Color-code direction column
        for i in range(1, len(table_data)):
            val = info["top_shap_drivers"][i-1][1]
            if val > 0:
                table.setStyle(TableStyle([
                    ("TEXTCOLOR", (2, i), (2, i), HexColor("#dc2626")),
                ]))
            else:
                table.setStyle(TableStyle([
                    ("TEXTCOLOR", (2, i), (2, i), HexColor("#16a34a")),
                ]))

        card_elements.append(table)
        card_elements.append(Spacer(1, 5*mm))

        # ── Thin separator ──
        card_elements.append(HRFlowable(
            width="100%", thickness=0.5,
            color=HexColor("#e2e8f0"), spaceAfter=4*mm
        ))

        # Keep disease card together on same page
        elements.append(KeepTogether(card_elements))

    # ══════════════════════════════════════════
    #  EXTRACTED TEST VALUES
    # ══════════════════════════════════════════
    extracted_tests = result.get("extracted_tests", [])
    if extracted_tests:
        tests_label = "Extracted Test Values" if language == "en" else translate_text("Extracted Test Values")
        elements.append(Paragraph(f"<b>{tests_label}</b>", section_header_style))
        elements.append(Spacer(1, 2*mm))

        test_header = ["Test Name", "Value", "Unit"]
        if language == "hi":
            test_header = [translate_text(h) for h in test_header]

        test_data = [test_header]
        for t in extracted_tests:
            test_data.append([
                t.get("test", "—"),
                str(t.get("value", "—")),
                t.get("unit", "—"),
            ])

        test_table = Table(test_data, colWidths=[75*mm, 35*mm, 40*mm])
        test_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#334155")),
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(test_table)
        elements.append(Spacer(1, 8*mm))

    # ══════════════════════════════════════════
    #  FOOTER
    # ══════════════════════════════════════════
    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=HexColor("#d1d5db"), spaceAfter=3*mm
    ))

    disclaimer = (
        "This report is generated by MediReport AI for informational and screening purposes only. "
        "It is not a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare provider for clinical decisions."
    )
    if language == "hi":
        disclaimer = translate_text(disclaimer)
    elements.append(Paragraph(disclaimer, small_style))
    elements.append(Spacer(1, 2*mm))
    gen_by = "Generated by MediReport AI" if language == "en" else translate_text("Generated by MediReport AI")
    elements.append(Paragraph(gen_by, small_style))

    # ── Build PDF ──
    doc.build(elements)
    print(f"[OK] Report saved: {output_path}")


if __name__ == "__main__":
    with open("data/pipeline_output/full_result.json", "r") as f:
        result = json.load(f)

    os.makedirs("data/reports", exist_ok=True)

    generate_pdf_report(result, "data/reports/report_english.pdf", language="en")
    generate_pdf_report(result, "data/reports/report_hindi.pdf", language="hi")