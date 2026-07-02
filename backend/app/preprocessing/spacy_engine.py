#backend/app/preprocessing/spacy_engine.py
import spacy
from backend.app.core.resources import ResourceManager

from .base import PreprocessingEngine
from .config import PreprocessingConfig
from .processed_document import ProcessedDocument


class SpaCyPreprocessingEngine(PreprocessingEngine):
    def __init__(self, config: PreprocessingConfig):
        self.config = config
        self.nlp = ResourceManager.get_spacy_model(self.config.spacy_model)


    def process(self, text: str) -> ProcessedDocument:
        doc = self.nlp(text)

        terms = []
        pos_tags = []
        index_map = {}

        for token in doc:
            if token.is_space:
                continue

            if token.is_punct:
                continue

            if self.config.remove_stopwords and token.is_stop:
                continue

            term = token.text

            if self.config.lowercase:
                term = term.lower()

            if self.config.use_lemma:
                term = token.lemma_.lower()

            terms.append(term)

            index_map[token.i] = len(terms) - 1

            if self.config.keep_pos_tags:
                pos_tags.append(token.pos_)

        noun_chunks = None

        if self.config.keep_noun_chunks:

            noun_chunks = []

            for chunk in doc.noun_chunks:

                start = index_map.get(chunk.start)

                end = index_map.get(chunk.end - 1)

                if start is None or end is None:
                    continue

                noun_chunks.append((start, end))

        return ProcessedDocument(
            terms=terms,
            pos_tags=pos_tags if self.config.keep_pos_tags else None,
            noun_chunks=noun_chunks
        )