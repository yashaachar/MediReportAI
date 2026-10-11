from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
import traceback

from predict_pipeline import run_full_pipeline
from generate_report import generate_pdf_report

app = FastAPI(title="MediReport AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve the frontend (must be registered AFTER all API routes) ──
_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

TEMP_DIR = "temp"
REPORTS_DIR = "data/reports"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

RESULTS_CACHE = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_report(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now.")

    job_id = str(uuid.uuid4())
    temp_path = os.path.join(TEMP_DIR, f"{job_id}.pdf")

    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = run_full_pipeline(temp_path)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}\n\n{tb}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    RESULTS_CACHE[job_id] = result
    return {"job_id": job_id, **result}


@app.get("/result/{job_id}")
def get_analysis_result(job_id: str):
    if job_id not in RESULTS_CACHE:
        raise HTTPException(status_code=404, detail="No result found for this job_id.")
    return {"job_id": job_id, **RESULTS_CACHE[job_id]}


@app.get("/report/{job_id}")
def download_report(job_id: str, language: str = "en"):
    if job_id not in RESULTS_CACHE:
        raise HTTPException(status_code=404, detail="No result found for this job_id. Run /analyze first.")

    if language not in ("en", "hi"):
        raise HTTPException(status_code=400, detail="language must be 'en' or 'hi'.")

    result = RESULTS_CACHE[job_id]
    output_path = os.path.join(REPORTS_DIR, f"{job_id}_{language}.pdf")

    try:
        if not os.path.exists(output_path):
            generate_pdf_report(result, output_path, language=language)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        raise HTTPException(status_code=500, detail=f"PDF generation error: {type(e).__name__}: {e}")

    filename = "MediReport_English.pdf" if language == "en" else "MediReport_Hindi.pdf"
    return FileResponse(output_path, media_type="application/pdf", filename=filename)


# ── Static files (frontend) — mount LAST so API routes take precedence ──
if os.path.isdir(_FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")