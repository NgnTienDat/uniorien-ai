from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RAGDocument:
    """
    Đại diện cho một tài liệu thu được từ VectorDB.
    """
    id: str
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None

    def short(self, max_len=120):
        """
        Dùng để debug – xem đoạn text ngắn gọn.
        """
        if len(self.text) <= max_len:
            return self.text
        return self.text[:max_len] + "..."
