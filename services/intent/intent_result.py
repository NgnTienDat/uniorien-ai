from dataclasses import dataclass
from typing import Optional

from services.intent.intent import QueryIntent


@dataclass
class IntentResult:
    intent: QueryIntent
    confidence: float
    reason: Optional[str] = None
