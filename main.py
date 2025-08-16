from fastapi import FastAPI, UploadFile, File
from typing import List
import pytesseract, shutil, tempfile, os
from pdf2image import convert_from_path

app = FastAPI()

@app.post("/evaluate")
async def evaluate(
    qp: List[UploadFile] = File(..., description="Upload Question Paper files"),
    as_: List[UploadFile] = File(..., description="Upload Answer Sheet files")
):
    tmp_dir = tempfile.mkdtemp()
    qp_text, as_text = "", ""

    try:
        # Process Question Paper files
        for file in qp:
            path = os.path.join(tmp_dir, file.filename)
            with open(path, 'wb') as f:
                shutil.copyfileobj(file.file, f)

            if path.lower().endswith('.pdf'):
                images = convert_from_path(path)
                for img in images:
                    qp_text += pytesseract.image_to_string(img)
            else:
                qp_text += pytesseract.image_to_string(path)

        # Process Answer Sheet files
        for file in as_:
            path = os.path.join(tmp_dir, file.filename)
            with open(path, 'wb') as f:
                shutil.copyfileobj(file.file, f)

            if path.lower().endswith('.pdf'):
                images = convert_from_path(path)
                for img in images:
                    as_text += pytesseract.image_to_string(img)
            else:
                as_text += pytesseract.image_to_string(path)

        # --- Mock evaluation logic ---
        keywords = ["photosynthesis", "independence", "equation", "climate"]
        found = [k for k in keywords if k.lower() in as_text.lower()]
        missing = [k for k in keywords if k.lower() not in as_text.lower()]

        score = int((len(found) / len(keywords)) * 100) if keywords else 0

        return {
            "score": score,
            "strengths": [f"Used key term: {k}" for k in found] or ["Good attempt"],
            "fixes": [f"Missed explaining: {k}" for k in missing] or ["Try adding examples"],
            "lessons": ["Start answers with a definition", "Use diagrams if possible"],
            "plan": ["Revise missed key terms", "Practice writing structured answers"]
        }

    finally:
        shutil.rmtree(tmp_dir)
