from __future__ import annotations
from dataclasses import dataclass
from typing import List
from services.rag.rag_document import RAGDocument


@dataclass
class RAGResponse:
    """
    Output tiêu chuẩn của một RAG pipeline.
    """
    answer: str
    context_used: List[RAGDocument]

    def debug_context(self):
        """
        Trả về toàn bộ context để dễ kiểm tra.
        """
        lines = []
        for doc in self.context_used:
            lines.append(f"- ID: {doc.id} | Score: {doc.score}")
            lines.append(f"  Text: {doc.short()}")
        return "\n".join(lines)
