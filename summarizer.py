from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import os

from backend.model_pipeline import process_pdf_and_summarize
from fastapi import Depends
# from .auth import get_current_user
from backend.auth import get_current_user

import logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...), user: str = Depends(get_current_user)):
    logging.info("Summarize endpoint hit")
    try:
        print(f"[INFO] Authenticated user: {user}")
        print(f"[INFO] Received file: {file.filename}")

        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            content = await file.read()
            temp.write(content)
            temp_path = temp.name

        print(f"[INFO] Saved temp file at: {temp_path}")
        
        # Using a default query for summarization
        result = process_pdf_and_summarize(
            pdf_path=temp_path,
            query="Provide a detailed summary of the key legal points in this document"
        )

        os.remove(temp_path)
        print("[INFO] Removed temp file")

        if "error" in result:
            return JSONResponse(status_code=500, content={"error": result["error"]})
            
        return JSONResponse(content={
            "summary": result.get("result", ""),
            "sources": result.get("source_documents", [])
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
