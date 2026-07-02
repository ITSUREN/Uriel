# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.api.search import router as search_router
from backend.app.storage.factory import build_repositories

DB_PATH = "backend/app/data/uriel.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.doc_repo, app.state.index_repo = build_repositories(DB_PATH)
    yield

app = FastAPI(title="Uriel Search Engine", version="0.1.0", lifespan=lifespan)
app.include_router(search_router)