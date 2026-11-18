"""
FastAPI Application for Automated Multi-Platform Posting System.
"""

from typing import Optional
from fastapi import FastAPI, Query, status
from fastapi.responses import JSONResponse
from app.config import settings
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import posting_service

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description=(
        "Production-ready FastAPI service that automatically publishes short messages "
        "(up to 200 characters with exactly one CTA URL) across multiple social and broadcasting "
        "platforms (Bluesky, Mastodon, Telegram, Discord, Reddit) using official APIs."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", tags=["System"])
async def root():
    """
    Service health and information endpoint.
    """
    configured_platforms = [
        p.name for p in posting_service.platforms if p.is_configured()
    ]
    return {
        "service": "Automated Multi-Platform Posting System",
        "version": "1.0.0",
        "status": "operational",
        "mock_mode_default": settings.MOCK_MODE,
        "supported_platforms": [p.name for p in posting_service.platforms],
        "configured_platforms": configured_platforms,
        "docs_url": "/docs",
        "posting_endpoint": "POST /posting",
    }


@app.get("/platforms", tags=["System"])
async def get_platforms():
    """
    Lists all supported platforms with configuration status and public accessibility.
    """
    return {
        "platforms": [
            {
                "name": p.name,
                "public_access": p.is_public,
                "configured": p.is_configured(),
            }
            for p in posting_service.platforms
        ]
    }


@app.post(
    "/posting",
    response_model=PostingResponse,
    status_code=status.HTTP_200_OK,
    tags=["Posting"],
    summary="Publish a short message with CTA URL across all supported platforms",
    description=(
        "Publishes a validated message (<= 200 characters, containing exactly 1 valid CTA URL) "
        "across all supported platforms concurrently. Each platform is executed independently "
        "so that a failure on one platform does not interrupt or halt the others."
    ),
)
async def post_message(
    payload: PostingRequest,
    mock: Optional[bool] = Query(
        None,
        description="Override mock mode for testing without requiring live credentials (true/false).",
    ),
):
    # Determine whether mock mode should be used
    use_mock = mock if mock is not None else settings.MOCK_MODE

    response = await posting_service.publish_to_all(
        message=payload.message,
        cta_url=payload.cta_url,
        force_mock=use_mock,
    )

    return response
