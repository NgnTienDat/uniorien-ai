# service/ingestion/sources/postgres_information_source.py
from __future__ import annotations
from typing import List, Dict, Any
from components.manager import SQLDatabaseManager
from services.ingestion.sources.base_source import BaseIngestionSource, RawDocument


class PostgresInformationSource(BaseIngestionSource):
    """
    Ingest mô tả trường đại học từ bảng university_information.
    """

    QUERY = """
        SELECT
            university_id AS id,
            university_id,
            description AS text,
            updated_at AS created_at
        FROM university_information
        WHERE description IS NOT NULL AND TRIM(description) <> ''
    """

    def load(self) -> List[RawDocument]:
        db = SQLDatabaseManager.instance().get_db()
        rows = db.run(self.QUERY)

        documents = []
        for row in rows:
            doc_id = f"profile_{row['id']}"
            metadata = {
                "university_id": str(row["university_id"]),
                "type": "profile",
                "source_table": "university_information",
                "source_id": row["id"],
                "created_at": row.get("created_at"),
            }
            documents.append(RawDocument(id=doc_id, text=row["text"], metadata=metadata))

        return documents
