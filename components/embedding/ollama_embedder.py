from __future__ import annotations
from typing import List
import requests
from components.interfaces import IEmbedder


class OllamaEmbedder(IEmbedder):
    """
    Fallback embedder — sử dụng Ollama local embedding model.
    Hỗ trợ cả embed (single) và embed_batch (batch).
    """

    def __init__(self, model_name: str = "nomic-embed-text",
                 host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host.rstrip("/")

    def embed(self, text: str) -> List[float]:
        """
        Embed một chuỗi đơn lẻ.
        """
        if text is None or text == "":
            return []

        url = f"{self.host}/api/embeddings"
        payload = {"model": self.model_name, "input": text}
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Kỳ vọng: {"embeddings": [ [float], ... ]} hoặc {"embedding": [...]}
        if "embeddings" in data:
            return data["embeddings"][0]
        if "embedding" in data:
            return data["embedding"]
        # Fallback: empty vector
        return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed nhiều đoạn text cùng lúc.
        """
        if not texts:
            return []

        url = f"{self.host}/api/embeddings"
        payload = {"model": self.model_name, "input": texts}
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Kỳ vọng: {"embeddings": [ [float], ... ]}
        if "embeddings" in data:
            return data["embeddings"]
        # Nếu API trả embedding cho mỗi input dưới key khác, attempt to normalize:
        if isinstance(data, dict):
            # try to find a top-level list of lists
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], list):
                    return v  # best-effort
        # Fallback: return empty list
        return []
