# components/embedding/sentence_transformer_embedder.py
from __future__ import annotations
from typing import List

from sentence_transformers import SentenceTransformer
from components.interfaces import IEmbedder


class SentenceTransformerEmbedder(IEmbedder):

    def __init__(self, model_name: str = "AITeamVN/Vietnamese_Embedding"):
        # Tự động dùng GPU nếu có, không cần config phức tạp
        self.model = SentenceTransformer(
            model_name, device="cuda" if SentenceTransformer.is_cuda_available() else "cpu")

    def embed(self, text: str) -> List[float]:
        if not text or not text.strip():
            return []
        # normalize_embeddings=True → cosine similarity chính xác hơn trong Chroma
        vec = self.model.encode([text.strip()], normalize_embeddings=True, convert_to_numpy=True)
        return vec[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # Lọc text rỗng để tránh warning từ SentenceTransformer
        cleaned_texts = [t.strip() for t in texts if t and t.strip()]
        if not cleaned_texts:
            return [[] for _ in texts]

        embeddings = self.model.encode(
            cleaned_texts,
            normalize_embeddings=True,    # Quan trọng!
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=32,  # cố định hợp lý, không cần env
        )
        # Giữ đúng thứ tự gốc
        result = []
        cleaned_idx = 0
        for t in texts:
            if t and t.strip():
                result.append(embeddings[cleaned_idx].tolist())
                cleaned_idx += 1
            else:
                result.append([])
        return result