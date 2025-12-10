from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


# -----------------------------
# 1. Generator Interface (LLM)
# -----------------------------
class IGenerator(ABC):
    """
    Interface cho tất cả LLM providers (OpenAI, Ollama, v.v.)
    """

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Sinh output hoàn chỉnh từ LLM.
        Return: final text response từ LLM.
        """
        pass


# --------------------------------
# 2. Embedding Interface
# --------------------------------
class IEmbedder(ABC):
    """
    Interface embedding providers (SentenceTransformer, OpenAI embedding, v.v.)
    """

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Embed một đoạn text thành vector.
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed nhiều text cùng lúc (tối ưu cho ingestion).
        """
        pass


# --------------------------------
# 3. Vector Database Interface
# --------------------------------
class IVectorDatabase(ABC):
    """
    Interface cho Vector DB (ChromaDB hiện tại).
    """

    @abstractmethod
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Thêm documents vào DB.
        """
        pass

    @abstractmethod
    def query(
        self,
        embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query gần giống nhất.
        Return: dict chứa texts, ids, metadatas,...
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """
        Xoá documents theo ID.
        """
        pass


class ISQLDatabase(ABC):
    """
    Abstraction layer for SQL database access used by AI service.
    Implementation examples: PostgresDatabase, MySQLDatabase, SQLiteDatabase.
    """

    @abstractmethod
    def run(self, query: str) -> Any:
        """Execute SQL query and return result (DataFrame or list[dict])."""
        pass

    @abstractmethod
    def get_table_info(self, table_names: Optional[List[str]] = None) -> str:
        """Return table schema used for SQL Agent."""
        pass