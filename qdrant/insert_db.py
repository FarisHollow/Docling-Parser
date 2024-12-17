from qdrant.db_create import client, my_collection
import uuid
from fastapi import HTTPException
from qdrant_client import models

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
