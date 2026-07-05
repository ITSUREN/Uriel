#backend/app/schemas/document.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DocumentReponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    doc_id: int
    path: str
    title: str
    length: int
    last_modified: datetime

class BrowseEntryOut(BaseModel):
    name: str
    path: str
    is_dir: bool
    is_indexed: bool
    doc_id: int | None

class BrowseResponse(BaseModel):
    path: str | None
    entries: list[BrowseEntryOut]