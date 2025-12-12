from __future__ import annotations
from typing import List, Optional, Dict, Any

from components.manager import EmbeddingManager, VectorDatabaseManager
from services.rag.rag_document import RAGDocument


class RAGRetriever:
    """
    Retriever chuẩn cho UniOrien AI.
    - Embed query
    - Query Chroma
    - Convert sang list[RAGDocument]
    """

    def __init__(
        self,
        top_k: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        top_k: số kết quả muốn lấy
        filter_metadata: điều kiện filter khi hybrid (ví dụ filter theo university_id)
        """
        self.top_k = top_k
        self.filter_metadata = filter_metadata or {}

        # get embedder
        self.embedder = EmbeddingManager.instance().get_embedder()

        # get vector DB
        db_manager = VectorDatabaseManager.instance()
        if not db_manager.db:
            raise RuntimeError("VectorDatabaseManager is not configured.")
        self.vector_db = db_manager.db

    def retrieve(self, query: str) -> List[RAGDocument]:
        """
        Thực hiện RAG retrieve:
        1. Embed query
        2. Query VectorDB
        3. Convert thành list RAGDocument
        """
        if not query or not query.strip():
            return []

        # 1. Embed query
        query_emb = self.embedder.embed(query)

        # 2. Query Chroma
        if self.filter_metadata:
            result = self.vector_db.query(
                embedding=query_emb,
                n_results=self.top_k,
                where=self.filter_metadata,
            )
        else:
            result = self.vector_db.query(
                embedding=query_emb,
                n_results=self.top_k,
            )

        # result format (từ Chroma):
        # {
        #   "ids": [[...]],
        #   "documents": [[...]],
        #   "metadatas": [[...]],
        #   "distances": [[...]]
        # }

        ids = result.get("ids", [[]])[0]
        texts = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        documents: List[RAGDocument] = []
        for idx, doc_id in enumerate(ids):
            documents.append(
                RAGDocument(
                    id=doc_id,
                    text=texts[idx],
                    metadata=metadatas[idx],
                    score=distances[idx],  # cosine distance hoặc độ đo khác
                )
            )

        # 3. Sort theo score tăng dần (score thấp = gần hơn)
        documents.sort(key=lambda d: d.score if d.score is not None else 999)

        return documents
