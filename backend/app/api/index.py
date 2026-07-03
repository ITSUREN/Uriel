#backend/app/api/index.py
from fastapi import APIRouter, Depends
from backend.app.services.index_service import IndexService
from backend.app.api.deps import get_index_service

router = APIRouter(prefix="/index", tags=["index"])

@router.post("/build")
def build(svc: IndexService = Depends(get_index_service)):
    return svc.build()

@router.post("/rebuild")
def rebuild(svc: IndexService = Depends(get_index_service)):
    return svc.rebuild()

@router.get("/stats")
def stats(svc: IndexService = Depends(get_index_service)):
    return svc.stats()