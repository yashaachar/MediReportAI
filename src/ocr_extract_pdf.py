import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import os
import sys

_BASE = os.path.join(os.path.dirname(__file__), "..")
pytesseract.pytesseract.tesseract_cmd = os.path.join(_BASE, "tesseract-ocr", "tesseract.exe")
POPPLER_PATH = os.path.join(_BASE, "poppler", "poppler-26.02.0", "Library", "bin")

def pdf_to_images(pdf_path):
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH, dpi=300)
    return pages

def ocr_image(pil_image):
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_report.pdf"

    if not os.path.exists(pdf_path):
        print(f"⚠️ File not found: {pdf_path}")
    else:
        print(f"Processing: {pdf_path}")
        print("Converting PDF pages to images...")
        pages = pdf_to_images(pdf_path)
        print(f"Found {len(pages)} pages.")

        os.makedirs("data/ocr_output", exist_ok=True)
        full_text = ""

        for i, page in enumerate(pages):
            print(f"\nRunning OCR on page {i+1}/{len(pages)}...")
            text = ocr_image(page)
            full_text += f"\n===== PAGE {i+1} =====\n{text}"

        with open("data/ocr_output/sample_extracted.txt", "w", encoding="utf-8") as f:
            f.write(full_text)

        print("\n✅ Full extracted text saved to data/ocr_output/sample_extracted.txt")
        print("\n----- Preview of first 1000 characters -----")
        print(full_text[:1000])