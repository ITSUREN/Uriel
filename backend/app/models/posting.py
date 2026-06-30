from dataclasses import dataclass

@dataclass
class Posting:
    doc_id: int
    term_frequency: int
    positions: list[int]