import os
from llama_index.core import VectorStoreIndex
import openai
from dotenv import load_dotenv
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import models, AsyncQdrantClient
from qdrant_client.models import PayloadSchemaType
import qdrant_client
from llama_index.embeddings.fastembed import FastEmbedEmbedding
import numpy as np

if not load_dotenv():
    print("Warning: .env file not found!")
else:
    print("Successfully loaded .env file.")

openai.api_key = os.getenv("api_key")

if not openai.api_key:
    raise Exception("OpenAI API key not found. Please add it to your .env file.")

client = qdrant_client.QdrantClient()
aclient = AsyncQdrantClient(host="localhost", port=6333)
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
    print(f"Collection name: {my_collection} has been created")
else:
    print(f"Collection name: {my_collection} has been found")

#     see= client.scroll(
#     collection_name=my_collection,
#     limit=1,
#     with_vectors=True
# )
    
#     print("Show succeed", see)
    
async def embedding(nodes):
    
    embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")   
    embeddings = embed_model.get_text_embedding_batch(nodes)
    text_embed = embed_model.get_text_embedding(nodes)
    embeddings = [embeddings] if isinstance(embeddings[0], float) else embeddings
    print("Embedding shape:", np.array(embeddings).shape)
     
    return (embeddings, text_embed)
    

    
vector_store = QdrantVectorStore(client=client, aclient=aclient, enable_hybrid=True, batch_size=20, collection_name=my_collection)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

