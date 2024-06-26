from fastapi import FastAPI

from .chat.routes import router as chat_router

app = FastAPI(root_path="/v1")

app.include_router(chat_router, tags=["chat"])
