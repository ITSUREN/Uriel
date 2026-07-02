#backend/app/api/search.py
from fastapi import APIRouter, Depends
from backend.app.schemas.search import SearchRequest, SearchResponse
from backend.app.services.search_service import SearchService
from backend.app.api.deps import get_search_service

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", response_model=list[SearchResponse])
#TODO: might need to make it async in the future
def search(request: SearchRequest, svc: SearchService = Depends(get_search_service)):
    results = svc.search(request.query, request.algorithm, request.top_k)
    docs = svc.doc_repo.all()
    return [
        SearchResponse(
            doc_id = result.doc_id,
            score = result.score,
            snippet = result.snippet,
            title = docs[result.doc_id].title,
            path = docs[result.doc_id].path 
        )
        for result in results
    ]
