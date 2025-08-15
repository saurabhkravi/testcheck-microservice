from fastapi import FastAPI, File, UploadFile
import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF for PDF support

app = FastAPI()

async def extract_text_from_files(files):
    text_data = []
    for f in files:
        file_bytes = await f.read()
        if f.filename.lower().endswith('.pdf'):
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(pdf_doc)):
                pix = pdf_doc[page_num].get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                text_data.append(pytesseract.image_to_string(img))
        else:
            img = Image.open(io.BytesIO(file_bytes))
            text_data.append(pytesseract.image_to_string(img))
    return "\n".join(text_data)

@app.post("/evaluate")
async def evaluate(qp: list[UploadFile] = File(...), as_: list[UploadFile] = File(...)):
    qp_text = await extract_text_from_files(qp)
    as_text = await extract_text_from_files(as_)
    
    return {
        "question_paper_text": qp_text,
        "answer_sheet_text": as_text,
        "stats": {
            "qp_word_count": len(qp_text.split()),
            "as_word_count": len(as_text.split())
        }
    }
