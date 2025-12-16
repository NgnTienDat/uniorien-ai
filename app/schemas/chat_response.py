from pydantic import BaseModel
from typing import Any, Dict, Optional


class ChatResponse(BaseModel):
    answer: str
    intent: str
    data: Optional[Dict[str, Any]] = None
    debug: Optional[Dict[str, Any]] = None
