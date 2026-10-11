import streamlit as st
import sys
import os

# Allow importing from src/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from predict_pipeline import run_full_pipeline
from generate_report import generate_pdf_report

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="MediReport AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

RISK_STYLE = {
    "GREEN": {"emoji": "🟢", "color": "#1a9e5c", "bg": "#e8f8ef", "label": "Low Risk"},
    "YELLOW": {"emoji": "🟡", "color": "#b7791f", "bg": "#fff8e6", "label": "Moderate Risk"},
    "RED": {"emoji": "🔴", "color": "#d92d20", "bg": "#fdecea", "label": "High Risk"},
}
DEFAULT_STYLE = {"emoji": "⚪", "color": "#6b7280", "bg": "#f3f4f6", "label": "Unknown"}

# ----------------------------------------------------------------------------
# GLOBAL STYLES
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        #MainMenu, footer {visibility: hidden;}

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }

        /* Hero header */
        .hero {
            background: linear-gradient(120deg, #0f766e 0%, #14b8a6 100%);
            border-radius: 18px;
            padding: 2.2rem 2.5rem;
            color: white;
            margin-bottom: 1.8rem;
            box-shadow: 0 10px 30px rgba(15, 118, 110, 0.25);
        }
        .hero h1 {
            font-size: 2.1rem;
            font-weight: 800;
            margin: 0 0 0.3rem 0;
            color: white;
        }
        .hero p {
            font-size: 1.02rem;
            opacity: 0.92;
            margin: 0;
        }

        /* Section headers */
        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #14b8a6;
            margin: 1.6rem 0 0.8rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Patient info cards */
        .info-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .info-label {
            font-size: 0.8rem;
            color: #6b7280;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .info-value {
            font-size: 1.6rem;
            font-weight: 800;
            color: #111827;
            margin-top: 0.15rem;
        }

        /* Risk card */
        .risk-card {
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(0,0,0,0.06);
        }
        .risk-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .risk-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #111827;
        }
        .risk-badge {
            font-size: 0.85rem;
            font-weight: 700;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
        }
        .prob-bar-bg {
            background: rgba(0,0,0,0.08);
            border-radius: 999px;
            height: 10px;
            width: 100%;
            margin-top: 0.7rem;
            overflow: hidden;
        }
        .prob-bar-fill {
            height: 100%;
            border-radius: 999px;
        }

        .driver-row {
            display: flex;
            justify-content: space-between;
            padding: 0.35rem 0;
            border-bottom: 1px dashed #e5e7eb;
            font-size: 0.92rem;
        }
        .driver-row:last-child { border-bottom: none; }

        /* Upload zone */
        section[data-testid="stFileUploader"] {
            border: 2px dashed #99c9c3;
            border-radius: 14px;
            padding: 0.6rem;
            background: #f7fdfc;
        }

        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.55rem 1.4rem;
            border: none;
            background: #0f766e;
            color: white;
        }
        .stButton > button:hover {
            background: #0d5f58;
            color: white;
        }

        .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 700;
            background: #111827;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🩺 MediReport AI")
    st.caption("AI-assisted blood report analysis")
    st.markdown("---")
    st.markdown(
        """
        **How it works**
        1. Upload a blood report PDF
        2. OCR + extraction runs automatically
        3. Disease risk is predicted per condition
        4. Download a shareable PDF summary
        """
    )
    st.markdown("---")
    st.caption("⚠️ For informational purposes only. Not a substitute for professional medical diagnosis.")

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🩺 MediReport AI</h1>
        <p>Automated blood report analysis and disease risk prediction — upload a report and get clear, explainable results in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# UPLOAD
# ----------------------------------------------------------------------------
uploaded_file = st.file_uploader("Upload a blood report (PDF)", type=["pdf"])

if uploaded_file is not None:
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Processing report — running OCR, extracting values, predicting..."):
        result = run_full_pipeline(temp_path)

    st.success("✅ Analysis complete")

    # ---- Patient info ----
    patient = result["patient_info"]
    st.markdown('<div class="section-title">👤 Patient Information</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""<div class="info-card"><div class="info-label">Name</div>
            <div class="info-value">{patient.get("Name", "")}</div></div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="info-card"><div class="info-label">Age</div>
            <div class="info-value">{patient.get("Age", "N/A")}</div></div>""",
            unsafe_allow_html=True,
        )
    with col3:
        gender = "Male" if patient.get("Gender") == 1 else "Female"
       
        st.markdown(
            f"""<div class="info-card"><div class="info-label">Gender</div>
            <div class="info-value">{gender}</div></div>""",
            unsafe_allow_html=True,
        )

    # ---- Predictions ----
    st.markdown('<div class="section-title">🔬 Disease Risk Predictions</div>', unsafe_allow_html=True)

    for disease, info in result["predictions"].items():
        style = RISK_STYLE.get(info["risk_color"], DEFAULT_STYLE)
        status = "Positive" if info["prediction"] == 1 else "Negative"
        prob_pct = info["probability"] * 100

        st.markdown(
            f"""
            <div class="risk-card" style="background:{style['bg']};">
                <div class="risk-header">
                    <div class="risk-title">{style['emoji']} {disease} — {status}</div>
                    <div class="risk-badge" style="background:{style['color']};color:white;">
                        {style['label']} · {prob_pct:.1f}%
                    </div>
                </div>
                <div class="prob-bar-bg">
                    <div class="prob-bar-fill" style="width:{prob_pct}%; background:{style['color']};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"Details for {disease}"):
            if info.get("low_confidence"):
                st.warning("⚠️ Limited real report data available for this prediction — confidence is lower than usual.")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**✅ Data used from your report**")
                st.write(", ".join(info["real_data_features"]) if info["real_data_features"] else "None")
            with col_b:
                st.markdown("**🧮 Estimated / default values**")
                st.write(", ".join(info["default_features"]) if info["default_features"] else "None")

            st.markdown("**📊 Top contributing factors**")
            for feat, val in info["top_shap_drivers"]:
                direction = "↑ increases risk" if val > 0 else "↓ decreases risk"
                color = "#d92d20" if val > 0 else "#1a9e5c"
                st.markdown(
                    f"""<div class="driver-row"><span>{feat}</span>
                    <span style="color:{color}; font-weight:600;">{val:+.4f} ({direction})</span></div>""",
                    unsafe_allow_html=True,
                )

    # ---- Report download ----
    st.markdown('<div class="section-title">📄 Download Report</div>', unsafe_allow_html=True)

    lang_choice = st.radio("Select report language:", ["English", "Hindi"], horizontal=True)
    lang_code = "en" if lang_choice == "English" else "hi"

    if st.button("Generate PDF Report"):
        os.makedirs("data/reports", exist_ok=True)
        output_path = f"data/reports/report_{lang_code}.pdf"
        with st.spinner("Generating report..."):
            generate_pdf_report(result, output_path, language=lang_code)

        with open(output_path, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=f,
                file_name=f"MediReport_{lang_choice}.pdf",
                mime="application/pdf",
            )

    with st.expander("🔍 View raw extracted test values"):
        st.json(result["extracted_tests"])

else:
    st.markdown(
        """
        <div style="text-align:center; padding: 3rem 1rem; color:#6b7280;">
            <div style="font-size:2.4rem;">👆</div>
            <div style="font-size:1.05rem; margin-top:0.5rem;">Upload a blood report PDF to get started</div>
        </div>
        """,
        unsafe_allow_html=True,
    )