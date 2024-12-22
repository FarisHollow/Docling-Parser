import qdrant_client
from qdrant_client import models, AsyncQdrantClient




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
    
    
count = client.count(collection_name=my_collection).count
print(f"Total points in collection '{my_collection}': {count}")

# Get the number of vectors in the collection
response = client.count(collection_name=my_collection)
print(f"Number of vectors in the collection: {response.count}")    

#     see= client.scroll(
#     collection_name=my_collection,
#     limit=1,
#     with_vectors=True
# )
    
#     print("Show succeed", see)   