from threading import Lock
from datetime import datetime, timezone
from services.ingestion.status import IngestState, IngestStatus

class IngestStatusStore:
    _instance = None
    _lock = Lock()

    def __init__(self):
        self.status = IngestStatus()

    @classmethod
    def instance(cls) -> "IngestStatusStore":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def mark_running(self):
        self.status.state = IngestState.RUNNING
        self.status.started_at = datetime.now(timezone.utc)
        self.status.finished_at = None
        self.status.error = None

    def mark_success(self):
        self.status.state = IngestState.SUCCESS
        self.status.finished_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str):
        self.status.state = IngestState.FAILED
        self.status.finished_at = datetime.now(timezone.utc)
        self.status.error = error

    def get_status(self) -> IngestStatus:
        return self.status