from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from utils.dataset_utils import index
from utils.chat_history import chat_memory, chat_store, chat_store_path
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from utils.dataset_utils import search_context
import os
import openai

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established.")
    query_tool = QueryEngineTool.from_defaults(
        query_engine=index.as_chat_engine(),
        name="Data",
        description=("Provides information about all the data deeply. If you don't know the answer simply say,  'I have no clue' ",)
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
            
            enriched_query = await search_context(data=data)
            
    
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