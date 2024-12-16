from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from utils.dataset_utils import index
from utils.chat_history import chat_memory, chat_store, chat_store_path
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from utils.dataset_utils import client, my_collection
import os
import openai

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established.")
    query_tool = QueryEngineTool.from_defaults(
        query_engine=index.as_chat_engine(),
        name="Faris",
        description=("Provides information about Faris",)
    )

    llm = OpenAI(model='gpt-3.5-turbo')
    agent = ReActAgent.from_tools(
        llm=llm,
        tools=[query_tool],
        memory=chat_memory,
        verbose=True
    )
    
    try:
        while True:
            data = await websocket.receive_text() 
            print(f"User: {data}")
            
            await websocket.send_text(f"User: {data}")
            
            from llama_index.embeddings.fastembed import FastEmbedEmbedding
            
            embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")   
            embeddings = embed_model.get_text_embedding(data)

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

            print(f"Retrieved Context: {context}")
            
            enriched_query = f"Context:\n{context}\n\nUser Query:\n{data}"
            response = str(agent.chat(enriched_query))
            print(f"Reply: {response}")
            
            response = str(agent.chat(data))
            
            print(f"Reply: {response}")
            await websocket.send_text(f"Reply: {response}")
            
    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")




@router.get("/")
async def get():
    return FileResponse(os.path.join("view", "chat.html"))