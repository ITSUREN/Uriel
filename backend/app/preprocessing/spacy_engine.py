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

        pipe_names = set(self.nlp.pipe_names)
        # lemmatization needs POS internally (rule-based lemmatizer keys off
        # token.pos_), regardless of whether the caller wants POS *output*.
        needs_pos = self.config.use_lemma or self.config.keep_pos_tags

        to_disable = []
        # NER: never used anywhere in this pipeline, and it's one of the two
        # genuinely expensive components (~1GB/100k chars) — always off.
        if "ner" in pipe_names:
            to_disable.append("ner")
        # Parser: the other expensive component. Only noun_chunks needs it.
        if not self.config.keep_noun_chunks and "parser" in pipe_names:
            to_disable.append("parser")
        # Tagger/attribute_ruler: cheap, but skip if truly nothing needs POS.
        if not needs_pos:
            for pipe in ("tagger", "attribute_ruler"):
                if pipe in pipe_names:
                    to_disable.append(pipe)
        if not self.config.use_lemma and "lemmatizer" in pipe_names:
            to_disable.append("lemmatizer")

        self._disabled = to_disable
        if self.nlp.max_length < 2_000_000:
            self.nlp.max_length = 2_000_000

    def process(self, text: str) -> ProcessedDocument:
        with self.nlp.select_pipes(disable=self._disabled):
            doc = self.nlp(text)
        terms, pos_tags, index_map = [], [], {}
        for token in doc:
            if token.is_space or token.is_punct:
                continue
            if self.config.remove_stopwords and token.is_stop:
                continue
            term = token.lemma_.lower() if self.config.use_lemma else token.text
            if self.config.lowercase:
                term = term.lower()
            terms.append(term)
            index_map[token.i] = len(terms) - 1
            if self.config.keep_pos_tags:
                pos_tags.append(token.pos_)
        noun_chunks = None
        if self.config.keep_noun_chunks:
            noun_chunks = []
            for chunk in doc.noun_chunks:
                start, end = index_map.get(chunk.start), index_map.get(chunk.end - 1)
                if start is not None and end is not None:
                    noun_chunks.append((start, end))
        return ProcessedDocument(
            terms=terms,
            pos_tags=pos_tags if self.config.keep_pos_tags else None,
            noun_chunks=noun_chunks,
        )