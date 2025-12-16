from __future__ import annotations
from typing import Optional, List, Dict

from services.intent.intent import QueryIntent
from services.intent.intent_router import IntentRouter
from services.intent.intent_result import IntentResult

from services.rag.rag_service import RAGService
from services.sql_agent.sql_agent_service import SQLAgentService
from services.sql_agent.sql_answer_service import SQLAnswerService
from services.sql_agent.sql_result import SQLAgentResult
from services.rag.rag_response import RAGResponse
from services.hybrid.hybrid_answer_service import HybridAnswerService


class ChatOrchestrator:
    """
    Central query orchestrator for UniOrien AI.
    """

    def __init__(
        self,
        rag_service: Optional[RAGService] = None,
        sql_service: Optional[SQLAgentService] = None,
        hybrid_service: Optional[HybridAnswerService] = None,
        intent_router: Optional[IntentRouter] = None,
    ):
        self.rag_service = rag_service or RAGService()
        self.sql_service = sql_service or SQLAgentService()
        self.hybrid_service = hybrid_service or HybridAnswerService()
        self.intent_router = intent_router or IntentRouter()

    def handle_query(
        self,
        query: str,
        context: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:

        intent_result: IntentResult = self.intent_router.route(query)

        if intent_result.intent == QueryIntent.SQL:
            return self._handle_sql(query, intent_result)

        if intent_result.intent == QueryIntent.RAG:
            return self._handle_rag(query, intent_result)

        if intent_result.intent == QueryIntent.HYBRID:
            return self._handle_hybrid(query, intent_result)

        return self._handle_rag(query, intent_result)



    def _handle_sql(self, query: str, intent: IntentResult) -> Dict:
        sql_result: SQLAgentResult = self.sql_service.query(query)

        answer_service = SQLAnswerService()
        answer_text = answer_service.generate(
            question=query,
            sql_result=sql_result,
        )
        return {
            "answer": answer_text,
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

    def _handle_hybrid(self, query: str, intent: IntentResult) -> Dict:
        """
        Hybrid pipeline:
        SQL (ground truth) + RAG (context) → LLM synthesis
        """

        # 1. Execute SQL
        sql_result: SQLAgentResult = self.sql_service.query(query)

        # 2. Execute RAG (always, for explanation)
        rag_result: RAGResponse = self.rag_service.query(query)

        # 3. Nếu SQL rỗng → fallback RAG
        if sql_result.is_empty():
            return self._handle_rag(query, intent)

        # 4. Hybrid synthesis
        answer = self.hybrid_service.synthesize(
            question=query,
            sql_result=sql_result,
            rag_documents=rag_result.context_used,
        )

        return {
            "answer": answer,
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
