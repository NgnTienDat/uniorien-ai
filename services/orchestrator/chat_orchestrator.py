from __future__ import annotations
from typing import Optional, List, Dict

from services.intent.intent import QueryIntent
from services.intent.intent_router import IntentRouter
from services.intent.intent_result import IntentResult

from services.rag.rag_service import RAGService
from services.sql_agent.sql_agent_service import SQLAgentService
from services.sql_agent.sql_result import SQLAgentResult
from services.rag.rag_response import RAGResponse


class ChatOrchestrator:
    """
    Trung tâm điều phối xử lý query cho UniOrien AI.
    """

    def __init__(
        self,
        rag_service: Optional[RAGService] = None,
        sql_service: Optional[SQLAgentService] = None,
        intent_router: Optional[IntentRouter] = None,
    ):
        self.rag_service = rag_service or RAGService()
        self.sql_service = sql_service or SQLAgentService()
        self.intent_router = intent_router or IntentRouter()

    def handle_query(
        self,
        query: str,
        context: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        """
        Entry point chính cho /api/chat
        """

        intent_result: IntentResult = self.intent_router.route(query, context)

        if intent_result.intent == QueryIntent.SQL:
            return self._handle_sql(query, intent_result)

        if intent_result.intent == QueryIntent.RAG:
            return self._handle_rag(query, intent_result)

        if intent_result.intent == QueryIntent.HYBRID:
            # Tạm thời: fallback về RAG
            # (HYBRID sẽ mở rộng sau)
            return self._handle_rag(query, intent_result)

        return self._handle_rag(query, intent_result)

    # --------------------
    # Internal handlers
    # --------------------

    def _handle_sql(self, query: str, intent: IntentResult) -> Dict:
        sql_result: SQLAgentResult = self.sql_service.query(query)

        return {
            "answer": sql_result.to_human_text(),
            "intent": intent.intent.value,
            "data": {
                "sql": sql_result.sql,
                "columns": sql_result.columns,
                "rows": sql_result.rows,
            },
            "debug": {
                "confidence": intent.confidence,
                "reason": intent.reason,
            },
        }

    def _handle_rag(self, query: str, intent: IntentResult) -> Dict:
        rag_result: RAGResponse = self.rag_service.query(query)

        return {
            "answer": rag_result.answer,
            "intent": intent.intent.value,
            "context_used": [
                doc.metadata for doc in rag_result.context_used
            ],
            "debug": {
                "confidence": intent.confidence,
                "reason": intent.reason,
            },
        }
