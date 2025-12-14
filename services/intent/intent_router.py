from services.intent.intent import QueryIntent
from services.intent.intent_result import IntentResult


class IntentRouter:
    """
    Rule-based intent router for UniOrien AI (v2).

    Trách nhiệm:
    - Phân loại intent
    - Gán response_mode phù hợp
    - Không xử lý dữ liệu, không gọi service
    """

    SQL_KEYWORDS = [
        "bao nhiêu",
        "số lượng",
        "thống kê",
        "tỷ lệ",
        "trung bình",
        "cao nhất",
        "thấp nhất",
        "danh sách",
        "top",
        "so sánh",
        "điểm chuẩn",
    ]

    RAG_KEYWORDS = [
        "là gì",
        "giới thiệu",
        "lịch sử",
        "đánh giá",
        "ưu điểm",
        "nhược điểm",
        "thế nào",
        "ra sao",
    ]

    def route(self, query: str) -> IntentResult:
        q = query.lower()

        sql_score = sum(1 for kw in self.SQL_KEYWORDS if kw in q)
        rag_score = sum(1 for kw in self.RAG_KEYWORDS if kw in q)

        # Hybrid: includes data + explanation/analysis
        if sql_score > 0 and rag_score > 0:
            return IntentResult(
                intent=QueryIntent.HYBRID,
                confidence=0.85,
                reason="Query requires both structured data and explanation",
                response_mode="verbose",
            )

        if sql_score > 0:
            return IntentResult(
                intent=QueryIntent.SQL,
                confidence=0.9,
                reason="Detected statistical / quantitative intent",
                response_mode="compact",
            )

        return IntentResult(
            intent=QueryIntent.RAG,
            confidence=0.8,
            reason="Default to knowledge-based retrieval",
            response_mode="verbose",
        )
