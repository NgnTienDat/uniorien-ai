from __future__ import annotations
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from components.manager import EmbeddingManager, VectorDatabaseManager
from services.ingestion.sources.base_source import RawDocument


class IngestionService:
    """
    Generic ingestion pipeline: nhận list RawDocument, chunk → embed → lưu vào Chroma.
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
        B1 – full ingest: xóa collection trước.
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











# from __future__ import annotations
#
# import os
# import logging
# from typing import List, Dict, Any, Optional, Iterator
# from uuid import uuid4
#
# from langchain_text_splitters import RecursiveCharacterTextSplitter
#
# from components.manager import EmbeddingManager, VectorDatabaseManager
# from components.interfaces import IEmbedder, IVectorDatabase
#
# logger = logging.getLogger("uniorien.ingestion")
# if not logger.handlers:
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter("[Ingestion] %(asctime)s - %(message)s"))
#     logger.addHandler(handler)
#     logger.setLevel(logging.INFO)
#
#
# def _batch_iterable(items: List[Any], batch_size: int) -> Iterator[List[Any]]:
#     """Yield successive batches from items (preserve order)."""
#     for i in range(0, len(items), batch_size):
#         yield items[i : i + batch_size]
#
#
# class IngestionService:
#     """
#     Ingest text (.txt) into VectorDB via an Embedder.
#     - Uses a text splitter to create chunks.
#     - Embeds chunks in batches to avoid OOM / API limits.
#     - Stores chunks + embeddings + metadata in VectorDB.
#
#     Configuration notes:
#     - chunk_size / chunk_overlap tuned for Vietnamese long-form text.
#     - embed_batch_size adjustable (default 128).
#     - namespace or use_uuid can prevent ID collisions on re-ingest.
#     """
#
#     def __init__(
#         self,
#         chunk_size: int = 800,
#         chunk_overlap: int = 200,
#         embed_batch_size: int = 128,
#         namespace: Optional[str] = None,
#         use_uuid: bool = False,
#     ):
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             length_function=len,
#             separators=["\n\n", "\n", ". ", "? ", "! ", " "],
#         )
#
#         # Resolve embedder: prefer primary, fallback to fallback (from manager)
#         em_mgr = EmbeddingManager.instance()
#         self.embedder: IEmbedder = em_mgr.embedder or None  # manager uses attribute 'embedder'
#         if not self.embedder:
#             raise RuntimeError("EmbeddingManager chưa được configure with an embedder.")
#
#         # Resolve vector DB
#         self.vector_db: IVectorDatabase = VectorDatabaseManager.instance().db
#         if not self.vector_db:
#             raise RuntimeError("VectorDBManager chưa được configure with a vector DB.")
#
#         self.embed_batch_size = max(1, int(embed_batch_size))
#         self.namespace = namespace.strip() if namespace else None
#         self.use_uuid = bool(use_uuid)
#
#     # -------------------------
#     # File loading
#     # -------------------------
#     def load_text_from_file(self, file_path: str) -> str:
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"File không tồn tại: {file_path}")
#
#         if not file_path.lower().endswith(".txt"):
#             raise ValueError(f"Chỉ hỗ trợ file .txt: {file_path}")
#
#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read().strip()
#
#         if not content:
#             logger.warning("File rỗng: %s", file_path)
#         return content
#
#     # -------------------------
#     # ID helper
#     # -------------------------
#     def _make_chunk_id(self, base_name: str, idx: int) -> str:
#         if self.namespace:
#             prefix = f"{self.namespace}_{base_name}"
#         else:
#             prefix = base_name
#
#         if self.use_uuid:
#             # Add short UUID to avoid collisions across re-ingests
#             return f"{prefix}_{idx}_{uuid4().hex[:8]}"
#         else:
#             return f"{prefix}_{idx}"
#
#     # -------------------------
#     # Ingest single file
#     # -------------------------
#     def ingest_file(
#         self,
#         file_path: str,
#         extra_metadata: Optional[Dict[str, Any]] = None,
#         return_ids: bool = False,
#     ) -> Dict[str, Any]:
#         """
#         Ingest one text file into VectorDB.
#         Returns dict with 'file', 'num_chunks', and optionally 'ids'.
#         """
#         logger.info("Start ingest file: %s", file_path)
#         raw_text = self.load_text_from_file(file_path)
#         if not raw_text:
#             return {"file": file_path, "num_chunks": 0, "ids": [] if return_ids else None}
#
#         chunks = self.text_splitter.split_text(raw_text)
#         if not chunks:
#             logger.warning("No chunks created for file: %s", file_path)
#             return {"file": file_path, "num_chunks": 0, "ids": [] if return_ids else None}
#
#         logger.info("Created %d chunks from %s", len(chunks), file_path)
#
#         # Prepare metadata and ids lists aligned with chunks
#         base_name = os.path.basename(file_path)
#         ids: List[str] = []
#         metadatas: List[Dict[str, Any]] = []
#
#         for idx, _ in enumerate(chunks):
#             cid = self._make_chunk_id(base_name, idx)
#             ids.append(cid)
#             md: Dict[str, Any] = {
#                 "source_file": file_path,
#                 "source_name": base_name,
#                 "chunk_index": idx,
#             }
#             if extra_metadata:
#                 md.update(extra_metadata)
#             metadatas.append(md)
#
#         # Embed in batches and store incrementally
#         total_embedded = 0
#         embeddings_accumulator: List[List[float]] = []
#
#         for batch_idx, batch_chunks in enumerate(_batch_iterable(chunks, self.embed_batch_size)):
#             logger.info("Embedding batch %d (size=%d)...", batch_idx + 1, len(batch_chunks))
#             batch_embeddings = self.embedder.embed_batch(batch_chunks)
#             if not batch_embeddings or len(batch_embeddings) != len(batch_chunks):
#                 raise RuntimeError("Embedder returned unexpected result or batch size mismatch.")
#             embeddings_accumulator.extend(batch_embeddings)
#             total_embedded += len(batch_embeddings)
#
#         if total_embedded != len(chunks):
#             raise RuntimeError("Total embedded vectors != number of chunks (internal error).")
#
#         # Finally add documents to vector DB
#         logger.info("Adding %d documents to VectorDB...", len(chunks))
#         self.vector_db.add_documents(
#             texts=chunks,
#             embeddings=embeddings_accumulator,
#             metadatas=metadatas,
#             ids=ids,
#         )
#
#         logger.info("Ingest finished: %s → %d chunks", file_path, len(chunks))
#         result: Dict[str, Any] = {"file": file_path, "num_chunks": len(chunks)}
#         if return_ids:
#             result["ids"] = ids
#         return result
#
#     # -------------------------
#     # Ingest directory
#     # -------------------------
#     def ingest_directory(
#         self,
#         directory: str,
#         extra_metadata: Optional[Dict[str, Any]] = None,
#         return_summary: bool = True,
#     ) -> List[Dict[str, Any]]:
#         """
#         Ingest all .txt files in the directory. Deterministic ordering (sorted filenames).
#         Returns list of per-file results.
#         """
#         if not os.path.isdir(directory):
#             raise NotADirectoryError(f"Thư mục không tồn tại: {directory}")
#
#         results: List[Dict[str, Any]] = []
#         for filename in sorted(os.listdir(directory)):
#             if filename.lower().endswith(".txt"):
#                 file_path = os.path.join(directory, filename)
#                 res = self.ingest_file(file_path, extra_metadata=extra_metadata, return_ids=False)
#                 results.append(res)
#         if return_summary:
#             total = sum(r.get("num_chunks", 0) for r in results)
#             logger.info("Directory ingest completed: %s → %d files, %d chunks total", directory, len(results), total)
#         return results
#
#     # -------------------------
#     # Convenience CLI entry
#     # -------------------------
#     def run_cli(self) -> None:
#         """Entry point for CLI execution."""
#         import argparse
#
#         parser = argparse.ArgumentParser(description="Ingest TXT files into Chroma/VectorDB")
#         parser.add_argument("--dir", type=str, help="Directory containing .txt files")
#         parser.add_argument("--file", type=str, help="Single .txt file to ingest")
#         parser.add_argument("--namespace", type=str, default=None, help="Optional namespace for ids")
#         parser.add_argument("--uuid", action="store_true", help="Append short uuid to chunk ids")
#         parser.add_argument("--batch-size", type=int, default=self.embed_batch_size, help="Embed batch size")
#         args = parser.parse_args()
#
#         if args.namespace:
#             self.namespace = args.namespace
#         if args.uuid:
#             self.use_uuid = True
#         if args.batch_size:
#             self.embed_batch_size = max(1, int(args.batch_size))
#
#         if args.file:
#             self.ingest_file(args.file, extra_metadata=None, return_ids=False)
#         elif args.dir:
#             self.ingest_directory(args.dir, extra_metadata=None)
#         else:
#             parser.print_help()
