from __future__ import annotations

from components.manager import GenerationManager
from services.sql_agent.sql_result import SQLAgentResult


SQL_SYSTEM_PROMPT = """
    You are an academic assistant for Vietnamese university admissions.
    
    Rules:
    - The database result is the single source of truth.
    - Do NOT change, infer, aggregate, or invent numbers.
    - Do NOT repeat raw SQL queries.
    - If multiple rows exist, summarize them clearly.
    - If data is missing or duplicated, state it explicitly.
    
    Output:
    - Answer in clear, formal Vietnamese.
    - Be concise and factual.
    - Prefer bullet points or short paragraphs.
""".strip()


class SQLAnswerService:
    """
    Convert SQLAgentResult (structured data)
    into a natural language answer for end users.
    """

    def __init__(self):
        self.llm = GenerationManager.instance().primary
        if not self.llm:
            raise RuntimeError("GenerationManager is not configured.")

    def generate(
        self,
        question: str,
        sql_result: SQLAgentResult,
    ) -> str:
        """
        Generate a natural language answer from SQL result.
        """

        # Defensive fallback
        if sql_result.is_empty():
            return "Không có dữ liệu phù hợp để trả lời câu hỏi này."

        # Convert structured result to readable text
        sql_text = sql_result.to_human_text(max_rows=15)

        user_prompt = f"""
            Câu hỏi của người dùng:
            {question}

            Kết quả truy vấn từ cơ sở dữ liệu:
            {sql_text}

            Yêu cầu:
            - Trả lời trực tiếp câu hỏi
            - Không suy diễn ngoài dữ liệu
            - Nếu dữ liệu có nhiều dòng trùng lặp, hãy nêu rõ
        """.strip()

        return self.llm.generate(
            system_prompt=SQL_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=300,
        )
