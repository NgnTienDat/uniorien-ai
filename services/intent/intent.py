from enum import Enum

class QueryIntent(str, Enum):
    RAG = "rag"
    SQL = "sql"
    HYBRID = "hybrid"
