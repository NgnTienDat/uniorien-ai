from __future__ import annotations
from typing import List, Dict, Any, Optional
from components.interfaces import IVectorDatabase

import chromadb
from chromadb.config import Settings


class ChromaDB(IVectorDatabase):

    def __init__(
        self,
        persist_dir: str = "./data/chroma",
        collection_name: str = "uniorien_collection",
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        # Tạo client
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir,
            )
        )

        # Lấy hoặc tạo collection (không cung cấp embedding_function)
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

        if ids is None:
            ids = [str(i) for i in range(len(texts))]

        # Chroma yêu cầu mọi list phải cùng số lượng
        if len(texts) != len(embeddings):
            raise ValueError("texts và embeddings phải có cùng độ dài.")

        if metadatas and len(metadatas) != len(texts):
            raise ValueError("metadatas phải cùng độ dài với texts.")

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )


    def query(
        self,
        embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        if n_results < 1:
            n_results = 1
        if n_results > 100:
            n_results = 100

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where,
            include=["documents", "embeddings", "metadatas", "distances", "ids"],
        )

        # Chroma trả về mảng 2D — ta lấy hàng đầu tiên
        return {
            "ids": results.get("ids", [[]])[0],
            "documents": results.get("documents", [[]])[0],
            "metadatas": results.get("metadatas", [[]])[0],
            "distances": results.get("distances", [[]])[0],
        }

    def delete(self, ids: List[str]) -> None:
        self.collection.delete(ids=ids)
