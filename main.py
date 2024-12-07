from io import BytesIO
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, DocumentStream
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from typing import Annotated
from pathlib import Path
import qdrant_client 
import json
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from qdrant_client import models
import uuid
import numpy as np


app = FastAPI(debug=True)


client = qdrant_client.QdrantClient()
my_collection = "faris"
collections = client.get_collections()
existing_collections = [col.name for col in collections.collections]


# client.delete_collection(collection_name=my_collection)
# print("deleted")

if my_collection not in existing_collections:
    client.create_collection(
        collection_name=my_collection,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE, on_disk=True),
        optimizers_config=models.OptimizersConfigDiff(
            memmap_threshold=20000
        ),
    
    )
else:
    print(f"Collection name: {my_collection} has been found")

    see= client.scroll(
    collection_name=my_collection,
    limit=1,
    with_vectors=True
)
    
    print("Show succeed", see)
    
    
async def docling_parse(files):
    
    artifacts_path = StandardPdfPipeline.download_models_hf()
    pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    result = converter.convert(DocumentStream(name="file", stream=BytesIO(files)))  
    
    output = result.document.export_to_dict()
    json_output = json.dumps(output, indent=4)
    
    return json_output

        
async def embedding(json_output):
    embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    embeddings = embed_model.get_text_embedding(json_output)
    embeddings = [embeddings] if isinstance(embeddings[0], float) else embeddings
    print("Embedding shape:", np.array(embeddings).shape)
    return embeddings
    
    
async def insert_db(embeddings):
    
    embedding_ids = [str(uuid.uuid4()) for _ in embeddings]
    
    try:
        client.upsert(
            collection_name=my_collection,
            points=models.Batch(
                ids=embedding_ids,    
                vectors=embeddings,
            ),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
    
    print("Inserted data successfully")
        
    

@app.post("/upload/")
async def create(files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")]):
    

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    parse = await docling_parse(files=files[0].file.read())
    embed = await embedding(json_output=parse)
    await insert_db(embeddings=embed)
    
    return {"message": parse} 



@app.get("/", response_class=HTMLResponse)
async def frontend():
    file_path = Path(__file__).parent / "static" / "form.html"

    with open(file_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)

