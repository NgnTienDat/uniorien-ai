from __future__ import annotations
from typing import List
from services.rag.rag_document import RAGDocument


class RAGPromptBuilder:
    """
    Chuẩn hóa prompt cho RAG pipeline của UniOrien AI.
    """

    @staticmethod
    def build_context(documents: List[RAGDocument]) -> str:
        """
        Chuyển list RAGDocument → chuỗi context dùng cho LLM.
        """
        lines = []
        for doc in documents:
            meta = ", ".join([f"{k}: {v}" for k, v in doc.metadata.items()])
            lines.append(f"[Document ID: {doc.id} | Score: {doc.score} | {meta}]\n{doc.text}")
        return "\n\n".join(lines)

    @staticmethod
    def build_rag_prompt(query: str, documents: List[RAGDocument]):
        """
        Tạo prompt hoàn chỉnh để gửi đến LLM.
        """

        system_prompt = """
            Bạn là UniOrien AI — một hệ thống tư vấn tuyển sinh thông minh.
            Nhiệm vụ:
                - Trả lời câu hỏi của người dùng dựa 100% vào thông tin bối cảnh được cung cấp trong phần CONTEXT.
                - Nếu CONTEXT không chứa thông tin liên quan, chỉ nói rằng “Không tìm thấy thông tin phù hợp cho câu hỏi.”
                - Tuyệt đối không bịa, không suy luận nếu không có trong dữ liệu.
                - Trình bày câu trả lời rõ ràng, Tiếng Việt, súc tích nhưng đầy đủ.
        """.strip()
        context_block = RAGPromptBuilder.build_context(documents)

        user_prompt = f"""
            # CONTEXT
            {context_block}
            
            ---------------------
            # CÂU HỎI CỦA NGƯỜI DÙNG
            {query}
            
            ---------------------
            # YÊU CẦU TRẢ LỜI
            - Trả lời dựa hoàn toàn vào CONTEXT.
            - Không bịa đặt, không sử dụng kiến thức bên ngoài nếu CONTEXT không có.
            - Nếu context không chứa thông tin, hãy nói rõ: "Không tìm thấy dữ liệu phù hợp trong hệ thống."
            - Nếu có nhiều đoạn liên quan, hãy tổng hợp thành câu trả lời mạch lạc.
            - Hãy cố gắng sử dụng ngôn ngữ dễ hiểu với học sinh và phụ huynh.
            
            Câu trả lời:
        """.strip()
        return system_prompt, user_prompt
