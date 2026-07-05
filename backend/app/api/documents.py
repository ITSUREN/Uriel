#backend/app/api/documents.py
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.schemas.document import DocumentReponse, BrowseResponse
from backend.app.schemas.search import SearchResponse
from backend.app.services.document_service import DirectoryBrowseError, DocumentService
from backend.app.services.search_service import SearchService
from backend.app.api.deps import get_document_service, get_search_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("", response_model = list[DocumentReponse])
def list_documents(svc: DocumentService = Depends(get_document_service)):
    """
    List all documents in the system.
    """
    return svc.list_documents()


# Must be registered before /{doc_id} — otherwise FastAPI tries to parse
# "browse" as an int doc_id and returns a 422 instead of matching this route.
@router.get("/browse", response_model = BrowseResponse)
def browse(path: str | None = Query(None, description="Path to browse. If not provided, returns the watched directories."), svc: DocumentService = Depends(get_document_service)):
    """
    Browse the contents of a directory, scoped to watched directories.
    """
    try:
        return svc.browse(path)
    except DirectoryBrowseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{doc_id}", response_model = DocumentReponse)
def get_document(doc_id: int, svc: DocumentService = Depends(get_document_service)):
    """
    Get a document by its ID.
    """
    doc = svc.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found.")
    return doc

@router.get("/{doc_id}/related", response_model=list[SearchResponse])
def related_documents(doc_id: int, top_k: int = 5, svc: SearchService = Depends(get_search_service)):
    """
    Get documents related to the specified document ID.
    """ 
    try:
        results = svc.related(doc_id, top_k=top_k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return [
        SearchResponse(doc_id=r.doc_id, score=r.score, snippet=r.snippet, title=r.title, path=r.path)
        for r in results
    ]