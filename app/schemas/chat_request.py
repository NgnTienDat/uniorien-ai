from pydantic import BaseModel
from typing import Optional, List, Dict


class ChatRequest(BaseModel):
    query: str
    context: Optional[List[Dict[str, str]]] = None
