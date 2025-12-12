# service/ingestion/sources/postgres_information_source.py
from __future__ import annotations
from typing import List, Dict, Any
from components.manager import SQLDatabaseManager
from services.ingestion.sources.base_source import BaseIngestionSource, RawDocument


class PostgresInformationSource(BaseIngestionSource):

    QUERY = """
        SELECT
            id,
            university_id,
            about AS text,
            created_at,
            founded,
            institution_type,
            location,
            name,
            programs_offered,
            students,
            website_address
        FROM university_information
        WHERE about IS NOT NULL AND TRIM(about) <> ''
    """

    def load(self) -> List[RawDocument]:
        db = SQLDatabaseManager.instance().get_db()
        rows: List[Dict[str, Any]] = db.run(self.QUERY)

        documents: List[RawDocument] = []
        for row in rows:
            doc_id = f"profile_{row['id']}"
            metadata = {
                "university_id": str(row["university_id"]),
                "type": "profile",
                "source_table": "university_information",
                "source_id": row["id"],
                "created_at": str(row.get("created_at")),
                "founded": str(row.get("founded")),
                "institution_type": row.get("institution_type"),
                "location": row.get("location"),
                "name": row.get("name"),
                "programs_offered": row.get("programs_offered"),
                "students": row.get("students"),
                "website_address": row.get("website_address"),
            }
            documents.append(RawDocument(id=doc_id, text=row["text"], metadata=metadata))

        return documents
