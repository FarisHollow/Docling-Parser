from fastapi import FastAPI
import contextlib 
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from service import chat, doc


@contextlib.asynccontextmanager
async def lifespan(app):
    yield 

app = FastAPI(lifespan=lifespan, debug=True)



app.mount("/view", StaticFiles(directory="view"), name="static")
app.include_router(doc.router)
app.include_router(chat.router)
