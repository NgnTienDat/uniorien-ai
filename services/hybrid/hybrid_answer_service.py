from __future__ import annotations

from typing import List

from components.manager import GenerationManager
from services.sql_agent.sql_result import SQLAgentResult
from services.rag.rag_document import RAGDocument


HYBRID_SYSTEM_PROMPT = """
    You are an academic assistant for Vietnamese university admissions.
    
    Rules:
    - Structured data from the database is the single source of truth.
    - Do NOT change, infer, or invent numbers.
    - Use retrieved documents only for explanation or context.
    - If information is missing or incomplete, state it clearly.
    
    Output:
    - Answer in clear, formal Vietnamese.
    - Be concise, factual, and accurate.
""".strip()


class HybridAnswerService:
    """
    Synthesize SQL (structured data) + RAG (context)
    into a final user-facing answer.
    """

    def __init__(self):
        self.llm = GenerationManager.instance().primary
        if not self.llm:
            raise RuntimeError("GenerationManager is not configured.")

    def synthesize(
        self,
        question: str,
        sql_result: SQLAgentResult,
        rag_documents: List[RAGDocument],
    ) -> str:
        """
        Generate final hybrid answer.
        """

        # Defensive fallback
        if sql_result.is_empty() and not rag_documents:
            return "Không có đủ dữ liệu để trả lời câu hỏi này."

        sql_text = sql_result.to_human_text(max_rows=10)

        rag_context = ""
        if rag_documents:
            parts = []
            for idx, doc in enumerate(rag_documents, start=1):
                parts.append(
                    f"[Nguồn {idx}]\n{doc.text}"
                )
            rag_context = "\n\n".join(parts)

        user_prompt = f"""
            Câu hỏi của người dùng:
            {question}
            
            Dữ liệu có cấu trúc (từ cơ sở dữ liệu):
            {sql_text}
            
            Ngữ cảnh bổ sung (từ tài liệu):
            {rag_context}
            
            Yêu cầu:
            - Trả lời dựa trên dữ liệu có cấu trúc
            - Chỉ dùng tài liệu để giải thích hoặc bổ sung bối cảnh
            - Không suy đoán nếu thiếu dữ liệu
        """.strip()

        return self.llm.generate(
            system_prompt=HYBRID_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=512,
        )
