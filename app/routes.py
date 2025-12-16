from fastapi import APIRouter, HTTPException

from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse
from services.orchestrator.chat_orchestrator import ChatOrchestrator

router = APIRouter(tags=["Chat"])



@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    orchestrator = ChatOrchestrator()
    try:
        result = orchestrator.handle_query(
            query=request.query,
            context=request.context,
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing chat request.",
        )
