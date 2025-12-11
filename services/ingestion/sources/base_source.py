# service/ingestion/sources/base_source.py
from __future__ import annotations
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class RawDocument:
    id: str
    text: str
    metadata: Dict[str, Any]


class BaseIngestionSource:
    """
    Interface cho mọi nguồn ingestion (PostgreSQL, File,...)
    """

    def load(self) -> List[RawDocument]:
        raise NotImplementedError("load() must be implemented in subclasses")
