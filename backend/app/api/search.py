#backend/app/api/search.py
from fastapi import APIRouter, Depends
from backend.app.schemas.search import SearchRequest, SearchResponse, FeedbackRequest
from backend.app.services.search_service import SearchService
from backend.app.api.deps import get_search_service

router = APIRouter(prefix="/search", tags=["search"])

def _to_out(results, docs):
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
#TODO: might need to make it async in the future
@router.post("", response_model=list[SearchResponse])
def search(request: SearchRequest, svc: SearchService = Depends(get_search_service)):
    results = svc.search(request.query, request.algorithm, request.top_k, request.expand_query)
    docs = svc.doc_repo.all()
    return _to_out(results, docs)

@router.post("/feedback", response_model=list[SearchResponse])
def feedback(request: FeedbackRequest, svc: SearchService = Depends(get_search_service)):
    results = svc.search_with_feedback(request.query, request.relevant_doc_ids, request.non_relevant_doc_ids, request.algorithm, request.top_k)
    docs = svc.doc_repo.all()
    return _to_out(results, docs)
