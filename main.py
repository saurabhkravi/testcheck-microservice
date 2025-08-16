from fastapi import FastAPI, UploadFile, File
from typing import List

app = FastAPI()

@app.post("/evaluate")
async def evaluate(
    qp: List[UploadFile] = File(...),
    as_: List[UploadFile] = File(...)
):
    return {
        "status": "success",
        "files_received": {
            "question_papers": [file.filename for file in qp],
            "answer_sheets": [file.filename for file in as_],
        }
    }
