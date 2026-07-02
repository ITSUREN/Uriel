#backend/app/preprocessing/base.py
from abc import ABC, abstractmethod

from .processed_document import ProcessedDocument


class PreprocessingEngine(ABC):

    @abstractmethod
    def process(self, text: str) -> ProcessedDocument:
        pass