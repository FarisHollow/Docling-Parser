from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from typing import Annotated
from pathlib import Path
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from qdrant_client import models
import uuid
import numpy as np
import contextlib 
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from chat import chat


@contextlib.asynccontextmanager
async def lifespan(app):
    yield 

app = FastAPI(lifespan=lifespan, debug=True)


@app.post("/upload/")
async def create(files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")]):
    
    from utils.dataset_utils import docling_parse, chunking, embedding
    

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    parse, clean_output  = await docling_parse(files=files[0].file.read())

    print(type(clean_output), "Cleaned output type")
    chunk = await chunking(output=clean_output)
    embed = await embedding(nodes=chunk)
   
    from qdrant.insert_db import insert_db

    await insert_db(embeddings=embed, payloads=chunk)
    
    return {"message": parse} 



@app.get("/doc", response_class=HTMLResponse)
async def frontend():
    file_path = Path(__file__).parent / "view" / "doc.html"

    with open(file_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


app.mount("/view", StaticFiles(directory="view"), name="static")


app.include_router(chat.router)