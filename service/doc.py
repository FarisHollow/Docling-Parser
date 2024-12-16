from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Annotated
from utils.dataset_utils import embedding, docling_parse, chunking
from qdrant.insert_db import insert_db
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()


@router.post("/upload/")
async def create(files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")]):
    

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    parse, clean_output  = await docling_parse(files=files[0].file.read())
    payloads=clean_output
    chunk = await chunking(output=parse)
    embed, _ = await embedding(nodes=chunk)
    await insert_db(embeddings=embed, payloads=payloads)
    
    return {"message": parse} 


@router.get("/doc", response_class=HTMLResponse)
async def frontend():
    file_path = Path(__file__).parent / "view" / "doc.html"

    with open(file_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)