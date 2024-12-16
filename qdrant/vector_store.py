from qdrant.db_create import client, aclient, my_collection 
from llama_index.vector_stores.qdrant import QdrantVectorStore 
from llama_index.core import VectorStoreIndex
 
vector_store = QdrantVectorStore(client=client, aclient=aclient, enable_hybrid=True, batch_size=20, collection_name=my_collection)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)