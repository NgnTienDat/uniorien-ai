from dataclasses import dataclass
from typing import Optional, Literal

from services.intent.intent import QueryIntent


ResponseMode = Literal["compact", "verbose"]

@dataclass(slots=True)
class IntentResult:
    """
        Kết quả phân loại intent của user query.

        - intent: loại câu hỏi (SQL / RAG / HYBRID)
        - confidence: độ tin cậy (0.0 - 1.0)
        - reason: giải thích ngắn gọn vì sao chọn intent này
        - response_mode: cách trình bày kết quả mong muốn
            - compact: ngắn gọn, trực tiếp (user-facing)
            - verbose: giàu ngữ cảnh (LLM / hybrid-facing)
        """
    intent: QueryIntent
    confidence: float
    response_mode: ResponseMode
    reason: Optional[str] = None
