from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from qdrant.vector_store import index
from utils.chat_history import chat_memory
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import os


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
            
            from utils.dataset_utils import search_context 
            enriched_data = await search_context(data)
            

            response = str(agent.chat(enriched_data))
            print(f"Reply: {response}")
            await websocket.send_text(f"Reply: {response}")
            
    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")




@router.get("/")
async def get():
    return FileResponse(os.path.join("view", "chat.html"))