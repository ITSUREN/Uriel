#backend/app/services/document_service.py
from pathlib import Path

from backend.app.models.document import Document
from backend.app.storage.base import DocumentRepository, DirectoryRepository

class DirectoryBrowseError(Exception):
    pass

class DocumentService:
    def __init__(self, doc_repo: DocumentRepository, directory_repo: DirectoryRepository):
        self.doc_repo = doc_repo
        self.directory_repo = directory_repo

    def list_documents(self) -> list[Document]:
        return list(self.doc_repo.all().values())
    
    def get_document(self, doc_id: int) -> Document | None:
        return self.doc_repo.get(doc_id)
    
    def browse(self, path: str | None) -> dict:
        """List the contents of a directory, scoped to watched directories.
        path=None returns the watched directories themselves (the "root" view).
        """
        watched = self.directory_repo.list()
        if not watched:
            return {"path": None, "entries": []}

        if path is None:
            entries = [{
                "name": Path(watch["path"]).name or watch["path"],
                "path": watch["path"],
                "is_dir": True,
                "is_indexed": False,
                "doc_id": None
            } for watch in watched
            ]
            return {"path": None, "entries": entries}
        
        resolved = Path(path).expanduser().resolve()
        self._assert_within_watched(resolved, watched)

        if not resolved.is_dir():
            raise DirectoryBrowseError(f"Path is not a directory: {resolved}")
        
        indexed_by_path = {doc.path: doc for doc in self.doc_repo.all().values()}

        entries = []
        for child in sorted(resolved.iterdir(), key = lambda p: (p.is_file(), p.name.lower())):
            if child.is_dir():
                entries.append({
                    "name": child.name,
                    "path": str(child),
                    "is_dir": True,
                    "is_indexed": False,
                    "doc_id": None
                })
            elif child.suffix.lower() in (".pdf", ".txt"):
                doc = indexed_by_path.get(str(child))
                entries.append({
                    "name": child.name,
                    "path": str(child),
                    "is_dir": False,
                    "is_indexed": doc is not None,
                    "doc_id": doc.doc_id if doc else None
                })
        return {"path": str(resolved), "entries": entries}
    
    def _assert_within_watched(self, resolved: Path, watched: list[dict]) -> None:
        for watch in watched:
            try:
                resolved.relative_to(Path(watch["path"]).resolve())
                return
            except ValueError:
                continue
        raise DirectoryBrowseError(f"Path is not within any watched directory: {resolved}")