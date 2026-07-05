# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import search, index, config as config_api, documents
from backend.app.api.deps import get_repositories, get_index_service
from backend.app.config.settings import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_repositories()  # warms the shared cache: connects, applies schema, seeds default dir
    if get_settings().auto_index_on_startup:
        get_index_service().build()
    yield

app = FastAPI(title="Uriel Search Engine", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(index.router)
app.include_router(config_api.router)
app.include_router(documents.router)