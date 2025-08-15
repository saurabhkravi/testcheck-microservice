from fastapi import FastAPI, UploadFile, File
from typing import List
import pytesseract, shutil, tempfile, os
from pdf2image import convert_from_path
from weasyprint import HTML

app = FastAPI()

@app.post("/evaluate")
async def evaluate(qp: List[UploadFile] = File(...), as_: List[UploadFile] = File(...)):
    tmp_dir = tempfile.mkdtemp()
    qp_text, as_text = "", ""
    try:
        for file in qp:
            path = os.path.join(tmp_dir, file.filename)
            with open(path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            if path.endswith('.pdf'):
                images = convert_from_path(path)
                for img in images:
                    qp_text += pytesseract.image_to_string(img)
            else:
                qp_text += pytesseract.image_to_string(path)
        for file in as_:
            path = os.path.join(tmp_dir, file.filename)
            with open(path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            if path.endswith('.pdf'):
                images = convert_from_path(path)
                for img in images:
                    as_text += pytesseract.image_to_string(img)
            else:
                as_text += pytesseract.image_to_string(path)
        score = 75
        strengths = ["Good keyword coverage"]
        fixes = ["Add examples"]
        pdf_html = f"<h1>Report</h1><p>Score: {score}%</p>"
        HTML(string=pdf_html).write_pdf(os.path.join(tmp_dir, 'report.pdf'))
        return {
            'score': score,
            'strengths': strengths,
            'fixes': fixes,
            'analysis': ["Placeholder analysis"],
            'lessons': ["Always start with a definition"],
            'plan': ["Revise weak topics"]
        }
    finally:
        shutil.rmtree(tmp_dir)
