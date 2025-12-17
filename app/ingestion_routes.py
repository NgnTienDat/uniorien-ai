import os
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException

from app.schemas.ingest import IngestStatusResponse
from app.utils import ApiResponse
from services.ingestion.ingest_status_store import IngestStatusStore
from services.ingestion.ingestion_service import IngestionService
from services.ingestion.sources.postgres_comments_source import PostgresCommentsSource
from services.ingestion.sources.postgres_information_source import PostgresInformationSource

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Ingestion"])




@router.post("", response_model = ApiResponse)
def ingest_data(
    background_tasks: BackgroundTasks,
    x_admin_token: str = Header(...),
):
    expected_token = os.getenv("ADMIN_INTERNAL_SECRET_KEY")

    if not expected_token or x_admin_token != expected_token:
        logger.error("Invalid admin token provided for ingestion")
        return ApiResponse(
            success=False,
            message="Invalid admin token",
        )

    def run_ingestion():
        store = IngestStatusStore.instance()
        store.mark_running()

        try:
            # ingestion = IngestionService()
            # sources = [
            #     PostgresCommentsSource(),
            #     PostgresInformationSource(),
            # ]
            # ingestion.ingest_sources(sources)
            store.mark_success()
            # raise ValueError("IngestionService is not implemented in this environment.")
        except Exception as e:
            store.mark_failed(str(e))
            logger.exception("Ingestion failed")

    background_tasks.add_task(run_ingestion)

    return ApiResponse(
        success=True,
        message="Ingestion started in background",
    )


@router.get("/status", response_model=ApiResponse[IngestStatusResponse])
def get_ingest_status():
    status = IngestStatusStore.instance().get_status()

    return ApiResponse(
        success=True,
        data=IngestStatusResponse(
            state=status.state.value,
            started_at=status.started_at,
            finished_at=status.finished_at,
            error=status.error,
        ),
    )
