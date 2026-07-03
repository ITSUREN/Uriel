#backend/app/services/config_service.py
from pathlib import Path
from dataclasses import asdict
from backend.app.preprocessing.config import PreprocessingConfig
from backend.app.storage.base import ConfigRepository, DirectoryRepository

DEFAULT_CONFIG = {
    "preprocessing": asdict(PreprocessingConfig()),
    "ranking" : {
        "default_algorithm": "bm25",
        "default_top_k": 10,
        "bm25": {
            "k1": 1.5,
            "b": 0.75
        },
    },
    "query_expansion": {
        "wordnet_enabled": False, #opt-in but doesn't have sense disambiguation yet
        "wordnet_max_synonyms_per_term": 2,
        "wordnet_synonym_weight": 0.5,
        "rocchio": {
            "alpha": 1.0,
            "beta": 0.75,
            "gamma": 0.15
        }
    }
}

class DirectoryValidationError(Exception):
    pass

class ConfigService:
    def __init__(self, config_repo: ConfigRepository, directory_repo: DirectoryRepository, allowed_root: str | None = None):
        self.config_repo = config_repo
        self.directory_repo = directory_repo
        # Security Lowered here so as to allow for different directories to be indexed, but still prevent arbitrary file access. If allowed_root is None, no restriction is applied.
        self.allowed_root = Path(allowed_root).resolve() if allowed_root else None

    def get(self) -> dict:
        return self.config_repo.get() or DEFAULT_CONFIG
    
    def update_preprocessing(self, updates: dict) -> dict:
        current = self.get()
        current["preprocessing"].update({
            k: v for k, v in updates.items() if v is not None
        })
        self.config_repo.save(current)
        return current
    
    def update_ranking(self, updates: dict) -> dict:
        current = self.get()
        if updates.get("bm25"):
            current["ranking"]["bm25"].update(updates.pop("bm25"))
        current["ranking"].update({
            k: v for k, v in updates.items() if v is not None
        })
        self.config_repo.save(current)
        return current
    
    def update_query_expansion(self, updates: dict) -> dict:
        current = self.get()
        if updates.get("rocchio"):
            current["query_expansion"]["rocchio"].update(updates.pop("rocchio"))
        current["query_expansion"].update({k: v for k, v in updates.items() if v is not None})
        self.config_repo.save(current)
        return current
    
    def list_directories(self) -> list[dict]:
        return self.directory_repo.list()
    
    def add_directory(self, path: str) -> dict:
        resolved = Path(path).expanduser().resolve()
        if not resolved.is_dir():
            raise DirectoryValidationError(f"Path is not a directory (or not visible to the backend): {resolved}")
        if self.allowed_root is not None:
            try:
                resolved.relative_to(self.allowed_root)
            except ValueError:
                raise DirectoryValidationError(f"Directory must be under the mounter root: {self.allowed_root}")
        return self.directory_repo.add(str(resolved))
    
    def remove_directory(self, dir_id: int) -> None:
        self.directory_repo.delete(dir_id)
        