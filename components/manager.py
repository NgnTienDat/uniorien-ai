from __future__ import annotations
import os
from typing import Optional, Dict

from components.interfaces import ISQLDatabase
from interfaces import IGenerator, IEmbedder, IVectorDatabase


class GenerationManager:
    """
    Quản lý các LLM providers: OpenAI (main), Ollama (fallback).
    """

    _instance: Optional["GenerationManager"] = None

    def __init__(self):
        self.primary: Optional[IGenerator] = None
        self.fallback: Optional[IGenerator] = None

    @classmethod
    def instance(cls) -> "GenerationManager":
        if cls._instance is None:
            cls._instance = GenerationManager()
        return cls._instance

    def configure(self, primary: IGenerator, fallback: Optional[IGenerator] = None):
        self.primary = primary
        self.fallback = fallback

    def generate(self, **kwargs) -> str:
        if self.primary is None:
            raise RuntimeError("GenerationManager is not configured with primary generator.")

        try:
            return self.primary.generate(**kwargs)
        except Exception as e:
            if self.fallback:
                print(f"[WARN] Primary LLM failed ({type(e).__name__}), switching to fallback...")
                return self.fallback.generate(**kwargs)
            raise RuntimeError(f"Primary LLM failed and no fallback available: {e}")


class EmbeddingManager:
    """
    Quản lý embedder (SentenceTransformer).
    """

    _instance: Optional["EmbeddingManager"] = None

    def __init__(self):
        self.embedder: Optional[IEmbedder] = None

    @classmethod
    def instance(cls) -> "EmbeddingManager":
        if cls._instance is None:
            cls._instance = EmbeddingManager()
        return cls._instance

    def configure(self, embedder: IEmbedder):
        self.embedder = embedder

    def embed(self, text: str):
        if not self.embedder:
            raise RuntimeError("EmbeddingManager is not configured.")
        return self.embedder.embed(text)

    def embed_batch(self, texts: list[str]):
        if not self.embedder:
            raise RuntimeError("EmbeddingManager is not configured.")
        return self.embedder.embed_batch(texts)


class VectorDBManager:
    """
    Quản lý vector database (ChromaDB).
    """

    _instance: Optional["VectorDBManager"] = None

    def __init__(self):
        self.db: Optional[IVectorDatabase] = None

    @classmethod
    def instance(cls) -> "VectorDBManager":
        if cls._instance is None:
            cls._instance = VectorDBManager()
        return cls._instance

    def configure(self, db: IVectorDatabase):
        self.db = db

    def add_documents(self, **kwargs):
        if not self.db:
            raise RuntimeError("VectorDBManager is not configured.")
        return self.db.add_documents(**kwargs)

    def query(self, **kwargs):
        if not self.db:
            raise RuntimeError("VectorDBManager is not configured.")
        return self.db.query(**kwargs)

    def delete(self, ids: list[str]):
        if not self.db:
            raise RuntimeError("VectorDBManager is not configured.")
        return self.db.delete(ids)


class PromptManager:
    """
    Tải và cache prompt .txt từ thư mục /prompt.
    """

    _instance: Optional["PromptManager"] = None

    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.base_path = os.path.join(os.getcwd(), "prompt")
        # self.base_path = os.path.join(os.path.dirname(__file__), "..", "prompt")

    @classmethod
    def instance(cls) -> "PromptManager":
        if cls._instance is None:
            cls._instance = PromptManager()
        return cls._instance

    def load(self, name: str) -> str:
        """
        name: tên file không kèm path (vd: 'intent_classification.txt')
        """
        if name in self.cache:
            return self.cache[name]

        file_path = os.path.join(self.base_path, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        self.cache[name] = content
        return content


class SQLDatabaseManager:
    """
    Singleton manager for the SQL database instance.

    Responsibilities:
    - Hold a single instance of ISQLDatabase.
    - Ensure the database is configured before being used.
    - Provide global access point for SQL-related operations in AI service.
    """

    _instance: Optional["SQLDatabaseManager"] = None

    def __init__(self):
        self.db: Optional[ISQLDatabase] = None

    @classmethod
    def instance(cls) -> "SQLDatabaseManager":
        if cls._instance is None:
            cls._instance = SQLDatabaseManager()
        return cls._instance

    def configure(self, db: ISQLDatabase) -> None:
        """
        Configure the database. Must be called once during app startup.
        """
        self.db = db

    def is_configured(self) -> bool:
        return self.db is not None

    def get_db(self) -> ISQLDatabase:
        """
        Return the configured database instance.
        Raise detailed error if database is not ready.
        """
        if not self.db:
            raise RuntimeError(
                "SQLDatabaseManager is not configured. "
                "Call SQLDatabaseManager.instance().configure(PostgresDatabase(...)) first."
            )
        return self.db