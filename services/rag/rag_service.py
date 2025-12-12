from __future__ import annotations
from typing import List

from components.manager import GenerationManager
from services.rag.retriever import RAGRetriever
from services.rag.rag_response import RAGResponse
from services.rag.rag_document import RAGDocument
from services.rag.prompt_template import RAGPromptBuilder


class RAGService:
    """
    RAG pipeline chính cho UniOrien AI:
    - Retrieve context từ Vector DB
    - Build prompt
    - Gọi LLM generate câu trả lời
    - Trả về RAGResponse
    """

    def __init__(self, top_k: int = 3):
        self.retriever = RAGRetriever(top_k=top_k)
        self.llm = GenerationManager.instance()

    def query(self, question: str) -> RAGResponse:
        """
        Thực thi full RAG.
        """
        if not question or not question.strip():
            return RAGResponse(
                answer="Không có câu hỏi hợp lệ.",
                context_used=[]
            )

        # 1. Retrieve
        docs: List[RAGDocument] = self.retriever.retrieve(question)

        # Nếu không có context
        if len(docs) == 0:
            return RAGResponse(
                answer="Không tìm thấy dữ liệu phù hợp trong hệ thống.",
                context_used=[]
            )

        # 2. Build prompt
        system_prompt, user_prompt = RAGPromptBuilder.build_rag_prompt(
            query=question,
            documents=docs
        )

        # 3. Call LLM
        answer = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )


        # Trả kết quả chuẩn hóa
        return RAGResponse(
            answer=answer,
            context_used=docs
        )
