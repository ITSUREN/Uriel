# backend/app/schemas/config.py
from pydantic import BaseModel
from backend.app.preprocessing.config import PreprocessingEngineType
from backend.app.algorithms.ranking_factory import RankingAlgorithmType

class PreprocessingConfigOut(BaseModel):
    engine: PreprocessingEngineType
    spacy_model: str
    lowercase: bool
    remove_stopwords: bool
    use_lemma: bool
    use_stemming: bool
    keep_pos_tags: bool
    keep_noun_chunks: bool

class PreprocessingConfigUpdate(BaseModel):
    engine: PreprocessingEngineType | None = None
    spacy_model: str | None = None
    lowercase: bool | None = None
    remove_stopwords: bool | None = None
    use_lemma: bool | None = None
    use_stemming: bool | None = None
    keep_pos_tags: bool | None = None
    keep_noun_chunks: bool | None = None

class BM25ConfigOut(BaseModel):
    k1: float
    b: float

class BM25ConfigUpdate(BaseModel):
    k1: float | None = None
    b: float | None = None

class RankingConfigOut(BaseModel):
    default_algorithm: RankingAlgorithmType
    default_top_k: int
    bm25: BM25ConfigOut

class RankingConfigUpdate(BaseModel):
    default_algorithm: RankingAlgorithmType | None = None
    default_top_k: int | None = None
    bm25: BM25ConfigUpdate | None = None

class RocchioConfigOut(BaseModel):
    alpha: float
    beta: float
    gamma: float

class RocchioConfigUpdate(BaseModel):
    alpha: float | None = None
    beta: float | None = None
    gamma: float | None = None

class QueryExpansionConfigOut(BaseModel):
    wordnet_enabled: bool
    wordnet_max_synonyms_per_term: int
    wordnet_synonym_weight: float
    spelling_correction_enabled: bool
    rocchio: RocchioConfigOut

class QueryExpansionConfigUpdate(BaseModel):
    wordnet_enabled: bool | None = None
    wordnet_max_synonyms_per_term: int | None = None
    wordnet_synonym_weight: float | None = None
    spelling_correction_enabled: bool | None = None
    rocchio: RocchioConfigUpdate | None = None

class DirectoryOut(BaseModel):
    id: int
    path: str
    is_default: bool

class DirectoryCreate(BaseModel):
    path: str

class AppConfigOut(BaseModel):
    preprocessing: PreprocessingConfigOut
    ranking: RankingConfigOut
    query_expansion: QueryExpansionConfigOut
    directories: list[DirectoryOut]