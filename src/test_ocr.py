import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"D:\MediReportAI\tesseract-ocr\tesseract.exe"

print(pytesseract.get_tesseract_version())