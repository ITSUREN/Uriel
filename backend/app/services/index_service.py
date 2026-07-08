#backend/app/services/index_service.py
from backend.app.index.indexer import Indexer
from backend.app.storage.base import DirectoryRepository
from backend.app.query_expansion.spell_correction import SpellCorrector
from backend.app.index.progress import IndexProgressTracker, IndexProgressSnapshot
import logging
import threading

logger = logging.getLogger(__name__)

class IndexService:
    def __init__(self, indexer: Indexer, 
                directory_repo:DirectoryRepository, 
                spell_corrector: SpellCorrector | None = None, 
                progress_tracker: IndexProgressTracker | None = None):
        self.indexer = indexer
        self.directory_repo = directory_repo
        self.spell_corrector = spell_corrector
         # Falls back to a fresh tracker if none is injected, so this class
        # still works standalone (e.g. in tests) -- but in the real app,
        # deps.py always injects the single shared singleton (see below),
        # since progress has to survive across separate per-request
        # IndexService instances.
        self.progress_tracker = progress_tracker or IndexProgressTracker()

    # ---- synchronous versions: unchanged behavior, now progress-aware ----
    def build(self, progress: IndexProgressTracker | None = None) -> dict:
        before = len(self.indexer.doc_repo.all())
        directories = self.directory_repo.list()
        if progress:
            total = sum(1 for d in directories for _ in self.indexer.iter_indexable_files(d["path"]))
            progress.set_total(total)
        for d in directories:
            self.indexer.index_directory(d["path"], progress=progress)
        after = len(self.indexer.doc_repo.all())
        if self.spell_corrector:
            self.spell_corrector.invalidate()
        return {"indexed": after - before, "total_documents": after}
    
    def rebuild(self, progress: IndexProgressTracker | None = None) -> dict:
        self.indexer.index_repo.clear()
        directories = self.directory_repo.list()
        if progress:
            total = sum(1 for d in directories for _ in self.indexer.iter_indexable_files(d["path"]))
            progress.set_total(total)
        for d in directories:
            self.indexer.index_directory(d["path"], progress=progress)
        if self.spell_corrector:
            self.spell_corrector.invalidate()
        return {"reindexed": len(self.indexer.doc_repo.all())}

    # ---- async entry points: what api/index.py actually calls ----
    def _run_async(self, target) -> bool:
        """
        Tried to claim the run via progress_tracker.try_strt() -- this is
        what makes it safe against two concurrent build/rebuild requests:
        try_start() atomically acquires an internal lock and returns False
        if a run is already in progress, so a second request gets a clean
        "already running" (409) instaed of two indexing runs racing each
        other or corrupting the same SQLite tables concurrently"""
        if not self.progress_tracker.try_start():
            return False
        
        def _run():
            try:
                target(progress = self.progress_tracker)
            except Exception as e:
                logger.exception("Indexing run failed")
                self.progress_tracker.finish(error=str(e))
            else:
                self.progress_tracker.finish()

        # dameon=True matters specifically for `uvicorn --reload`: when the
        # reloader restarts the worker proces on a file change, a daemon
        # thread is killed along with it insted of keep the old
        # process alive in the background
        threading.Thread(target=_run, daemon = True, name="index-worker").start()
        return True
    
    def start_build_async(self) -> bool:
        """Returns False if a build/rebuild is already running (caller
        should respond 409 Conflict, as api/index.py already does)."""
        return self._run_async(self.build)

    def start_rebuild_async(self) -> bool:
        return self._run_async(self.rebuild)

    def progress(self) -> IndexProgressSnapshot:
        return self.progress_tracker.snapshot()

    def stats(self) -> dict:
        docs = self.indexer.doc_repo.all()
        return {
            "documents": len(docs),
            "vocabulary_size": self.indexer.index_repo.vocabulary_size(),
            "directories": self.directory_repo.list(),
        }