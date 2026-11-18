"""
Mastodon integration for federated microblogging.
Official API: Mastodon REST API v1 (POST /api/v1/statuses)
Documentation: https://docs.joinmastodon.org/methods/statuses/
"""

import uuid
import httpx
from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class MastodonPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Mastodon"

    @property
    def is_public(self) -> bool:
        return True

    def is_configured(self) -> bool:
        return bool(settings.MASTODON_ACCESS_TOKEN)

    async def post(self, message: str, cta_url: str) -> PlatformResult:
        """
        Publishes a public status to the configured Mastodon instance.
        """
        if not self.is_configured():
            return self.failure_result(
                "Missing credentials: Set MASTODON_ACCESS_TOKEN in environment."
            )

        instance_url = settings.MASTODON_INSTANCE_URL.rstrip("/")
        access_token = settings.MASTODON_ACCESS_TOKEN

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{instance_url}/api/v1/statuses",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "status": message,
                        "visibility": "public",
                    },
                )

                if response.status_code not in (200, 201):
                    try:
                        err_detail = response.json().get("error", response.text)
                    except Exception:
                        err_detail = response.text
                    return self.failure_result(f"Mastodon API error ({response.status_code}): {err_detail}")

                data = response.json()
                post_url = data.get("url")
                if not post_url:
                    post_url = f"{instance_url}/statuses/{data.get('id')}"

                return self.success_result(posted_url=post_url)

        except httpx.TimeoutException:
            return self.failure_result("Mastodon API request timed out after 15 seconds.")
        except httpx.RequestError as exc:
            return self.failure_result(f"Network error communicating with Mastodon: {str(exc)}")
        except Exception as exc:
            return self.failure_result(f"Unexpected error posting to Mastodon: {str(exc)}")

    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        instance = settings.MASTODON_INSTANCE_URL.rstrip("/") or "https://mastodon.social"
        mock_id = uuid.uuid4().hex[:10]
        return self.success_result(
            posted_url=f"{instance}/@demouser/mock-{mock_id}",
            is_mock=True,
        )
