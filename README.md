<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-FF6600?style=for-the-badge&logo=xgboost&logoColor=white" />
  <img src="https://img.shields.io/badge/Tesseract_OCR-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/SHAP-Explainability-blueviolet?style=for-the-badge" />
</p>

<h1 align="center">🩺 MediReport AI</h1>

<p align="center">
  <strong>AI-powered blood report analysis and disease risk prediction</strong><br/>
  Upload a blood report PDF → get instant risk predictions for <b>Diabetes</b>, <b>Heart Disease</b> & <b>Liver Disease</b> — with explainable AI insights.
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#%EF%B8%8F-tech-stack">Tech Stack</a> •
  <a href="#-project-structure">Project Structure</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-disclaimer">Disclaimer</a>
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **PDF Upload & OCR** | Reads scanned and digital blood report PDFs using Tesseract OCR + Poppler |
| 🧠 **NLP Extraction** | Regex + synonym-mapping engine that recognizes 50+ common blood tests across different lab formats |
| 🔬 **3 Disease Models** | Separate XGBoost classifiers for **Diabetes**, **Heart Disease**, and **Liver Disease** |
| 📊 **SHAP Explanations** | Every prediction shows the top contributing factors ranked by impact — fully explainable AI |
| 🎯 **Risk Color Coding** | Instant 🟢 Green / 🟡 Yellow / 🔴 Red risk signals with confidence indicators |
| 📑 **Bilingual PDF Reports** | Download a beautifully formatted summary in **English** or **Hindi** (हिंदी) |
| 🌐 **Two Frontends** | A premium glassmorphism **web UI** (vanilla HTML/CSS/JS) + a **Streamlit** dashboard |
| 🔒 **Privacy First** | Files are processed in-memory and deleted immediately — nothing is stored permanently |

---

## 🔄 How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. Upload   │────▶│  2. OCR +    │────▶│  3. ML Risk  │────▶│ 4. Download  │
│  Blood Report│     │  NLP Extract │     │  Prediction  │     │  PDF Report  │
│  (PDF)       │     │  (Tesseract) │     │  (XGBoost)   │     │  (EN / HI)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

1. **Upload** — Drop in any standard blood test report PDF (scanned or digital)
2. **OCR + Extraction** — Tesseract reads the pages; NLP engine identifies test names, values, and units across various lab formats
3. **AI Prediction** — Three independent XGBoost models predict risk. SHAP values explain which features drove the prediction
4. **Report** — Get a formatted PDF summary in English or Hindi to share with your doctor

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **OCR** | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) + [Poppler](https://poppler.freedesktop.org/) via `pdf2image` |
| **Image Processing** | OpenCV (`cv2`) + NumPy |
| **NLP / Extraction** | Custom regex engine with synonym mapping for 50+ blood tests |
| **ML Models** | XGBoost classifiers (Diabetes, Heart, Liver) |
| **Explainability** | SHAP (TreeExplainer) |
| **API** | FastAPI + Uvicorn |
| **Streamlit App** | Streamlit |
| **Web Frontend** | Vanilla HTML5 / CSS3 / JavaScript (glassmorphism design) |
| **PDF Generation** | ReportLab with Hindi font support (Noto Sans Devanagari) |
| **Translation** | `deep-translator` (Google Translate) for Hindi reports |

---

## 📁 Project Structure

```
MediReportAI/
├── src/                          # Core backend logic
│   ├── api.py                    # FastAPI REST API (main entry point)
│   ├── ocr_extract_pdf.py        # PDF → images → OCR text
│   ├── nlp_extract.py            # NLP engine: extract test values & patient info
│   ├── feature_mapping.py        # Map extracted tests → model feature vectors
│   ├── predict_pipeline.py       # Full pipeline: OCR → NLP → predict → SHAP
│   ├── generate_report.py        # PDF report generation (EN/HI)
│   ├── train_diabetes.py         # Train diabetes XGBoost model
│   ├── train_heart.py            # Train heart disease model
│   ├── train_liver.py            # Train liver disease model
│   ├── shap_explain.py           # SHAP summary plots
│   ├── clean_data.py             # Data preprocessing utilities
│   └── explore_data.py           # EDA helpers
│
├── app/
│   └── app.py                    # Streamlit dashboard (alternative UI)
│
├── frontend/                     # Premium web frontend
│   ├── index.html                # Main HTML page
│   └── assets/
│       ├── style.css             # Glassmorphism CSS with animations
│       └── app.js                # Upload, analyze, render results logic
│
├── models/                       # Pre-trained model artifacts
│   ├── diabetes_model.pkl
│   ├── heart_model.pkl
│   ├── liver_model.pkl
│   └── *_shap_summary.png       # SHAP feature importance plots
│
├── fonts/
│   └── NotoSansDevanagari-*.ttf  # Hindi font for PDF reports
│
├── data/
│   ├── raw/                      # Raw training datasets
│   ├── processed/                # Cleaned datasets
│   └── reports/                  # Generated PDF reports (runtime)
│
├── tesseract-ocr/                # Bundled Tesseract binary (Windows)
├── poppler/                      # Bundled Poppler binary (Windows)
│
├── start.bat                     # One-click server launcher (Windows)
├── serve_frontend.bat            # Frontend-only dev server
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Tesseract OCR** — bundled in `tesseract-ocr/` or [install separately](https://github.com/tesseract-ocr/tesseract#installing-tesseract)
- **Poppler** — bundled in `poppler/` or [install separately](https://poppler.freedesktop.org/)

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/MediReportAI.git
cd MediReportAI
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

**Option A — FastAPI + Web UI (recommended)**

```bash
# Windows (one-click)
start.bat

# Manual
cd src
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

Then open **http://127.0.0.1:8000** for the web UI, or **http://127.0.0.1:8000/docs** for interactive API docs.

**Option B — Streamlit Dashboard**

```bash
streamlit run app/app.py
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/analyze` | Upload a PDF and get full analysis (OCR + NLP + predictions + SHAP) |
| `GET` | `/result/{job_id}` | Retrieve cached analysis result |
| `GET` | `/report/{job_id}?language=en` | Download generated PDF report (`en` or `hi`) |

### Example: Analyze a report

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F "file=@blood_report.pdf"
```

<details>
<summary>📋 Sample response</summary>

```json
{
  "job_id": "a1b2c3d4-...",
  "patient_info": {
    "Name": "John Doe",
    "Age": 45,
    "Gender": 1
  },
  "extracted_tests": [
    { "test": "Hemoglobin", "value": 12.5, "unit": "g/dL" },
    { "test": "Fasting Blood Sugar", "value": 142, "unit": "mg/dL" },
    { "test": "Cholesterol", "value": 220, "unit": "mg/dL" }
  ],
  "predictions": {
    "Diabetes": {
      "prediction": 1,
      "probability": 0.782,
      "risk_color": "RED",
      "low_confidence": false,
      "top_shap_drivers": [
        ["Glucose", 0.4521],
        ["BMI", 0.1203],
        ["Age", 0.0891]
      ]
    }
  }
}
```

</details>

---

## 🧪 Training the Models

The models are pre-trained and saved in `models/`. To retrain:

```bash
cd src
python train_diabetes.py
python train_heart.py
python train_liver.py
```

Training data should be placed in `data/processed/` as cleaned CSVs.

---

## 🌍 Bilingual PDF Reports

Reports can be generated in **English** and **Hindi**. Hindi translation uses the `deep-translator` library (Google Translate API) and renders with the **Noto Sans Devanagari** font for proper script support.

---

## ⚠️ Disclaimer

> **MediReport AI is for informational and educational purposes only.**
> It is **not** a substitute for professional medical advice, diagnosis, or treatment.
> Always consult a qualified healthcare professional for medical decisions.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ for accessible healthcare intelligence
</p>
