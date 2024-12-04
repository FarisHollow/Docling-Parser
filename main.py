from io import BytesIO
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, DocumentStream
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated
from pathlib import Path
import qdrant_client 
from llama_index.vector_stores.qdrant import QdrantVectorStore
import json
from llama_index.embeddings.fastembed import FastEmbedEmbedding

app = FastAPI(debug=True)

embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

embeddings = embed_model.get_text_embedding("Some text to embed. And all i need to do is check Hope fully .")

client = qdrant_client.QdrantClient()

vector_store = QdrantVectorStore(
    collection_name="faris", client=client
)

print("Number of ",len(embeddings))
print(embeddings[:10]) 


@app.post("/upload/")
async def create(files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")]):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")


    artifacts_path = StandardPdfPipeline.download_models_hf()
    pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    result = converter.convert(DocumentStream(name="file", stream=BytesIO(files[0].file.read())))  
    output = result.document.export_to_dict()
    jason_output = json.dumps(output)

    print(jason_output)  


    return {"message": jason_output} 


    

@app.get("/", response_class=HTMLResponse)
async def frontend():
    file_path = Path(__file__).parent / "static" / "form.html"

    with open(file_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)

