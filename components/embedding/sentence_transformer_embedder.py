from __future__ import annotations
from typing import List
import torch
from sentence_transformers import SentenceTransformer
from components.interfaces import IEmbedder


class SentenceTransformerEmbedder(IEmbedder):

    def __init__(self, model_name: str = "AITeamVN/Vietnamese_Embedding"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=device)

    def embed(self, text: str) -> List[float]:
        if not text or not text.strip():
            return []
        vec = self.model.encode(
            [text.strip()],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vec[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        cleaned = [t.strip() for t in texts if t and t.strip()]
        if not cleaned:
            return [[] for _ in texts]

        embeddings = self.model.encode(
            cleaned,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=32,
        )

        result = []
        idx = 0
        for t in texts:
            if t and t.strip():
                result.append(embeddings[idx].tolist())
                idx += 1
            else:
                result.append([])
        return result
