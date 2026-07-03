#backend/app/api/index.py
from fastapi import APIRouter, Depends

from backend.app.api.deps import get_index_service
from backend.app.config.settings import get_settings
from backend.app.services.index_service import IndexService

router = APIRouter(prefix="/index", tags=["index"])

@router.post("/build")
def build_index(directory: str | None = None, svc: IndexService = Depends(get_index_service)):
    settings = get_settings()
    return svc.build(directory or settings.data_dir)


@router.get("/stats")
def index_stats(svc: IndexService = Depends(get_index_service)):
    return svc.stats()
