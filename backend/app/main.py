#backend/app/main.py
from fastapi import FastAPI
from backend.app.api.search import router as search_router

app = FastAPI(title="Uriel Search Engine", version="0.1.0")
app.include_router(search_router)