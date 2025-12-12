from __future__ import annotations
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from components.interfaces import IVectorDatabase


class ChromaDB(IVectorDatabase):

    def __init__(
        self,
        persist_directory: str = "./chroma_store",
        collection_name: str = "uniorien_ai",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # API mới – bạn bắt buộc phải dùng thế này
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Tạo hoặc lấy collection (Chroma mới dùng Metadata index)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def query(
        self,
        embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where,
        )
        return result

    def delete(self, ids: List[str]) -> None:
        """
        Nếu ids = [] → xóa toàn bộ collection.
        """
        if ids:
            self.collection.delete(ids=ids)
        else:
            self.client.delete_collection(self.collection_name)
            # tạo collection lại để những lần ingest sau không lỗi
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
