"""
Posting orchestration service.
Dispatches messages concurrently to all registered platforms with independent error handling.
"""

import asyncio
from typing import List
from app.config import settings
from app.platforms import ALL_PLATFORMS, BasePlatform
from app.schemas import PlatformResult, PostingResponse


class PostingService:
    def __init__(self, platforms: List[BasePlatform] = None):
        if platforms is not None:
            self.platforms = platforms
        else:
            self.platforms = [cls() for cls in ALL_PLATFORMS]

    async def _post_single(
        self, platform: BasePlatform, message: str, cta_url: str, force_mock: bool
    ) -> PlatformResult:
        """
        Executes a post on a single platform with complete isolation.
        Any unhandled exception is caught so other platforms are not affected.
        """
        try:
            if force_mock or settings.MOCK_MODE:
                return await platform.post_mock(message, cta_url)

            if not platform.is_configured():
                return platform.failure_result(
                    f"Platform credentials not configured in environment variables. "
                    f"Configure .env or set MOCK_MODE=true for testing."
                )

            return await platform.post(message, cta_url)

        except Exception as exc:
            return platform.failure_result(f"Unhandled platform error: {str(exc)}")

    async def publish_to_all(
        self, message: str, cta_url: str, force_mock: bool = False
    ) -> PostingResponse:
        """
        Publishes the message to all 5 platforms concurrently.
        Failures on one platform do not stop or impact others.
        """
        tasks = [
            self._post_single(platform, message, cta_url, force_mock=force_mock)
            for platform in self.platforms
        ]

        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Check if at least one platform succeeded
        has_success = any(r.status == "success" for r in results)

        return PostingResponse(
            success=has_success,
            results=list(results),
        )


# Global service instance
posting_service = PostingService()
