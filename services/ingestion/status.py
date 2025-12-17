from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class IngestState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class IngestStatus:
    state: IngestState = IngestState.IDLE
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
