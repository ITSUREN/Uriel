# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.config.settings import get_settings
from backend.app.api.index import router as index_router
from backend.app.api.search import router as search_router
from backend.app.index.indexer import Indexer
from backend.app.services.index_service import IndexService
from backend.app.storage.factory import build_repositories

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.doc_repo, app.state.index_repo = build_repositories(settings.db_path)

    if settings.auto_index_on_startup and not app.state.doc_repo.all():
        IndexService(Indexer(app.state.doc_repo, app.state.index_repo)).build(settings.data_dir)

    yield

app = FastAPI(title="Uriel Search Engine", version="0.1.0", lifespan=lifespan)
app.include_router(index_router)
app.include_router(search_router)