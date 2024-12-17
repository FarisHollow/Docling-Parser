from io import BytesIO
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, DocumentStream
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
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
from utils.dataset_utils import client, my_collection
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import Document
import qdrant_client

@contextlib.asynccontextmanager
async def lifespan(app):
    yield 

app = FastAPI(lifespan=lifespan, debug=True)


count = client.count(collection_name=my_collection).count
print(f"Total points in collection '{my_collection}': {count}")

# Get the number of vectors in the collection
response = client.count(collection_name=my_collection)
print(f"Number of vectors in the collection: {response.count}")


async def docling_parse(files):
    
    artifacts_path = StandardPdfPipeline.download_models_hf()
    pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    result = converter.convert(DocumentStream(name="file", stream=BytesIO(files)))  
    output = result.document.export_to_markdown()
    dict_output = result.document.export_to_dict()
    list_output = [child['orig'] for child in dict_output['texts'] if 'orig' in child]
    clean_output = '\n'.join(list_output)
    
    # keys = [f"key{i}" for i in range(1, len(clean_output) + 1)]


    # output_dict = dict(zip(keys, clean_output))
          
    # print(f"This is clean type {type(output_dict)}", output_dict)            


    return (output, clean_output)


async def chunking(output):
    
    text_splitter = TokenTextSplitter(
        chunk_size=1000,  # Number of tokens per chunk
        chunk_overlap=200,  
    )
    chunks = text_splitter.split_text(output)
    
    print(type(chunks), "This is type")
            
    return chunks



        
async def embedding(nodes):
    
    embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")   
    embeddings = embed_model.get_text_embedding_batch(nodes)
    embeddings = [embeddings] if isinstance(embeddings[0], float) else embeddings
    print("Embedding shape:", np.array(embeddings).shape)
    
  
    return embeddings
    
    
async def insert_db(embeddings, payloads):
    embedding_ids = [str(uuid.uuid4()) for _ in embeddings]
    print("This is len of payload: ", len(payloads))

    try:
        
        if len(payloads) != len(embeddings):
            raise ValueError("Number of payloads must match number of embeddings.")

        # Structure payloads to match the embeddings
        formatted_payloads = [{'text': text} for text in payloads]

     
        client.upsert(
            collection_name=my_collection,
            points=models.Batch(
                ids=embedding_ids,
                vectors=embeddings,
                payloads=formatted_payloads
            ),
        )
    except Exception as e:
        print(f"Error occurred during insertion: {str(e)}") 
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

    print("Inserted data successfully")

    
        
    

@app.post("/upload/")
async def create(files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")]):
    

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    parse, clean_output  = await docling_parse(files=files[0].file.read())
    
    # payloads=clean_output

    print(type(parse), " This is type")
    chunk = await chunking(output=clean_output)
    
    embed = await embedding(nodes=chunk)
    

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