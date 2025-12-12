from __future__ import annotations
from typing import List, Dict, Any
from components.manager import SQLDatabaseManager
from services.ingestion.sources.base_source import BaseIngestionSource, RawDocument


class PostgresNewsSource(BaseIngestionSource):
    QUERY = """
        SELECT
            id,
            university_id,
            content AS text,
            published_at AS created_at
        FROM news
        WHERE content IS NOT NULL AND TRIM(content) <> ''
    """

    def load(self) -> List[RawDocument]:
        db = SQLDatabaseManager.instance().get_db()
        rows = db.run(self.QUERY)

        documents = []
        for row in rows:
            doc_id = f"news_{row['id']}"
            metadata = {
                "university_id": str(row["university_id"]),
                "type": "news",
                "source_table": "news",
                "source_id": row["id"],
                "created_at": row.get("created_at"),
            }
            documents.append(RawDocument(id=doc_id, text=row["text"], metadata=metadata))

        return documents
