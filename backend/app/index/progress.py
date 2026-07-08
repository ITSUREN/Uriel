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