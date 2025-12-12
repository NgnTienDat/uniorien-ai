# service/ingestion/sources/postgres_comments_source.py
from __future__ import annotations
from typing import List, Dict, Any
from components.manager import SQLDatabaseManager
from services.ingestion.sources.base_source import BaseIngestionSource, RawDocument


class PostgresCommentsSource(BaseIngestionSource):
    QUERY = """
        SELECT 
            id,
            university_id,
            content AS text,
            created_at
        FROM university_comments
        WHERE content IS NOT NULL AND TRIM(content) <> ''
    """

    def load(self) -> List[RawDocument]:
        db = SQLDatabaseManager.instance().get_db()   # create or get existing connection
        rows: List[Dict[str, Any]] = db.run(self.QUERY)  # list[dict]

        documents: List[RawDocument] = []
        for row in rows:
            doc_id = f"review_{row['id']}"
            metadata = {
                "university_id": str(row["university_id"]),
                "type": "review",
                "source_table": "university_comments",
                "source_id": row["id"],
                "created_at": str(row.get("created_at")),
            }
            documents.append(RawDocument(id=doc_id, text=row["text"], metadata=metadata))

        return documents
