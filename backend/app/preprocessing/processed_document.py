#backend/app/preprocessing/processed_document.py
from dataclasses import dataclass

@dataclass(slots=True)
class ProcessedDocument:
    """
    Result produced by any preprocessing engine.

    terms:
        Final terms that should be indexed.

    pos_tags:
        Optional POS tags.

    noun_chunks:
        (start_index, end_index)
    """

    terms: list[str]

    pos_tags: list[str] | None = None

    noun_chunks: list[tuple[int, int]] | None = None