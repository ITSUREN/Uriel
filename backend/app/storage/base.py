#backend/app/storage/base.py
from abc import ABC, abstractmethod
from backend.app.models.document import Document
from backend.app.models.posting import Posting

class DocumentRepository(ABC):
    @abstractmethod
    def save(self, doc: Document) -> None: ...

    @abstractmethod
    def get(self, doc_id: int) -> Document | None: ...

    @abstractmethod
    def all(self) -> dict[int, Document]: ...

    @abstractmethod
    def exists_by_path(self, path: str) -> bool: ...

    @abstractmethod
    def next_id(self) -> int: ...

class IndexRepository(ABC):
    @abstractmethod
    def add_posting(self, term: str, postings: list[Posting]) -> None: ...

    @abstractmethod
    def get_postings(self, term: str) -> list[Posting]: ...

    @abstractmethod
    def vocabulary_size(self) -> int: ...

    @abstractmethod
    def clear(self) -> None: ...