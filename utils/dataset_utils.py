import os
from llama_index.core import VectorStoreIndex
import openai
from dotenv import load_dotenv
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import models, AsyncQdrantClient
from qdrant.db_create import client, my_collection, aclient
from llama_index.embeddings.fastembed import FastEmbedEmbedding
import numpy as np

if not load_dotenv():
    print("Warning: .env file not found!")
else:
    print("Successfully loaded .env file.")

openai.api_key = os.getenv("api_key")

if not openai.api_key:
    raise Exception("OpenAI API key not found. Please add it to your .env file.")


async def docling_parse(files):
    
    from io import BytesIO
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption, DocumentStream
    from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
    
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
              
    return (output, clean_output)


async def chunking(output):
    
    from llama_index.core.node_parser import TokenTextSplitter
    
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
    

async def search_context(data):
                 
        embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")   
        embeddings = embed_model.get_text_embedding(data)
        
        from qdrant.db_create import client, my_collection

        search_result = client.search(
               collection_name=my_collection,
               query_vector=embeddings,
               limit=3
            
              )        
    
        context = "\n".join(
                 text if isinstance(text, str) else " ".join(text)
                 for hit in search_result
                 for text in ([hit.payload['text']] if isinstance(hit.payload['text'], str) else hit.payload['text'])
             )

        # print(f"Retrieved Context: {context}")
            
        enriched_query = f"Context:\n{context}\n\nUser Query:\n{data}"
        
        return enriched_query
    


    
vector_store = QdrantVectorStore(client=client, aclient=aclient, enable_hybrid=True, batch_size=20, collection_name=my_collection)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

