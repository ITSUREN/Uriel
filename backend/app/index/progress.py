#backend/app/index/progress.py
import threading
import time
from dataclasses import dataclass, field
from enum import Enum

class IndexState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"

@dataclass
class SkippedFile:
    path:str
    reason: str

@dataclass
class IndexProgressSnapshot:
    state: IndexState
    total_files: int
    processed_files: int
    indexed_files: int
    current_file: str | None
    skipped: list
    error: str | None
    started_at: float | None
    finished_at: float | None

class IndexProgressTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._run_lock = threading.Lock()
        self._reset()

    def _reset(self):
        self._state = IndexState.IDLE
        self._total_files =  0
        self._processed_files = 0
        self._indexed_files = 0
        self._current_file = None
        self._skipped = []
        self._error = None
        self._started_at = None
        self._finished_at = None

    def try_start(self) -> bool:
        if not self._run_lock.acquire(blocking = False):
            return False
        with self._lock:
            self._reset()
            self._state = IndexState.RUNNING
            self._started_at = time.time()
        return True
    
    def set_total(self, total: int) -> None:
        with self._lock:
            self._total_files = total

    def file_started(self, path: str) -> None:
        with self._lock:
            self._current_file = path
    
    def file_indexed(self, path: str) -> None:
        with self._lock:
            self._processed_files +=1
            self._indexed_files +=1
            self._current_file = None
    
    def file_skipped(self, path: str, reason: str) -> None:
        with self._lock:
            self._processed_files += 1
            self._skipped.append(SkippedFile(path=path, reason=reason))
            self._current_file = None

    def finish(self, error: str | None = None) -> None:
        with self._lock:
            self._state = IndexState.ERROR if error else IndexState.DONE
            self._error = error
            self._current_file = None
            self._finished_at = time.time()
        self._run_lock.release()

    def snapshot(self) -> IndexProgressSnapshot:
        with self._lock:
            return IndexProgressSnapshot(
                state=self._state, 
                total_files=self._total_files,
                processed_files=self._processed_files, 
                indexed_files=self._indexed_files,
                current_file=self._current_file, 
                skipped=list(self._skipped),
                error=self._error, 
                started_at=self._started_at, 
                finished_at=self._finished_at,
            )