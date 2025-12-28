import logging

from fastapi import APIRouter, HTTPException, Request, Response

from app.rate_limit.identity import resolve_fingerprint, COOKIE_NAME
from app.rate_limit.limiter import check_rate_limit
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse
from services.orchestrator.chat_orchestrator import ChatOrchestrator

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(
        request: ChatRequest,
        http_request: Request,
        response: Response,
):

    fingerprint = resolve_fingerprint(http_request)
    print("Fingerprint:", fingerprint)
    print("Cookie:", COOKIE_NAME)

    if COOKIE_NAME not in http_request.cookies:
        response.set_cookie(
            key=COOKIE_NAME,
            value=fingerprint,
            httponly=True,
            max_age=60 * 60 * 24,  # 24h
            samesite="lax",
        )


    allowed = check_rate_limit(
        fingerprint=fingerprint,
        request=request,
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
        )

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
