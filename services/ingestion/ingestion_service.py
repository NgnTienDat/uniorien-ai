from __future__ import annotations
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from components.manager import EmbeddingManager, VectorDatabaseManager
from services.ingestion.sources.base_source import RawDocument


class IngestionService:
    """
    Generic ingestion pipeline: receive list RawDocument, chunk → embed → save into Chroma.
    """

    def __init__(self, chunk_size=800, chunk_overlap=200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        self.embedder = EmbeddingManager.instance().get_embedder()
        manager = VectorDatabaseManager.instance()
        if not manager.db:
            raise RuntimeError("VectorDatabaseManager is not configured.")
        self.vector_db = manager.db

    def ingest_sources(self, sources: List) -> None:
        """
        B1 – full ingest: delete old collection.
        """
        print("[Ingestion] Xóa toàn bộ dữ liệu trong collection...")
        self.vector_db.delete([])  # xóa toàn bộ collection (Chroma API)

        for source in sources:
            print(f"[Ingestion] Load data từ source: {source.__class__.__name__}")
            docs: List[RawDocument] = source.load()
            print(f"  → {len(docs)} bản ghi")

            all_chunks = []
            all_embeddings = []
            all_ids = []
            all_metadatas = []

            for doc in docs:
                chunks = self.splitter.split_text(doc.text)
                embeddings = self.embedder.embed_batch(chunks)

                for idx, chunk in enumerate(chunks):
                    chunk_id = f"{doc.id}_{idx}"
                    all_chunks.append(chunk)
                    all_embeddings.append(embeddings[idx])
                    # Convert datetime và các kiểu lạ về string
                    clean_meta = {}
                    for k, v in doc.metadata.items():
                        if isinstance(v, (int, float, bool)) or v is None:
                            clean_meta[k] = v
                        else:
                            clean_meta[k] = str(v)  # datetime → string, UUID → string, etc.

                    clean_meta["chunk_index"] = idx
                    all_metadatas.append(clean_meta)

                    all_ids.append(chunk_id)

            if all_chunks:
                print(f"  → Lưu {len(all_chunks)} chunks vào Chroma")
                self.vector_db.add_documents(
                    texts=all_chunks,
                    embeddings=all_embeddings,
                    metadatas=all_metadatas,
                    ids=all_ids,
                )