import os
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException

from services.ingestion.ingestion_service import IngestionService
from services.ingestion.sources.postgres_comments_source import PostgresCommentsSource
from services.ingestion.sources.postgres_information_source import PostgresInformationSource


router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("")
def ingest_data(
    background_tasks: BackgroundTasks,
    x_admin_token: str = Header(..., alias="x-admin-token"),
):
    expected_token = os.getenv("ADMIN_INTERNAL_SECRET_KEY")

    if not expected_token or x_admin_token != expected_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin internal token.",
        )

    def run_ingestion():
        ingestion = IngestionService()
        sources = [
            PostgresCommentsSource(),
            PostgresInformationSource(),
        ]
        ingestion.ingest_sources(sources)

    background_tasks.add_task(run_ingestion)

    return {
        "status": "accepted",
        "message": "Ingestion started in background",
    }
