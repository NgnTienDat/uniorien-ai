from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IngestStatusResponse(BaseModel):
    state: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error: Optional[str]
