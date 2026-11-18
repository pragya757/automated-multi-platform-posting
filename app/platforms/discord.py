"""
Discord Webhook integration for publishing messages to server channels.
Official API: Discord Webhook Execution (POST /api/webhooks/{id}/{token}?wait=true)
Documentation: https://discord.com/developers/docs/resources/webhook#execute-webhook
"""

import uuid
import httpx
from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DiscordPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Discord"

    @property
    def is_public(self) -> bool:
        # Discord channels require a Discord login to view
        return False

    def is_configured(self) -> bool:
        return bool(settings.DISCORD_WEBHOOK_URL)

    async def post(self, message: str, cta_url: str) -> PlatformResult:
        """
        Publishes a message to a Discord channel via Webhook.
        """
        if not self.is_configured():
            return self.failure_result(
                "Missing credentials: Set DISCORD_WEBHOOK_URL in environment."
            )

        webhook_url = settings.DISCORD_WEBHOOK_URL.strip()
        # Add wait=true query parameter so Discord returns the created message object
        separator = "&" if "?" in webhook_url else "?"
        execute_url = f"{webhook_url}{separator}wait=true"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    execute_url,
                    json={"content": message},
                )

                if response.status_code not in (200, 204):
                    try:
                        err_detail = response.json().get("message", response.text)
                    except Exception:
                        err_detail = response.text
                    return self.failure_result(f"Discord API error ({response.status_code}): {err_detail}")

                data = response.json() if response.status_code == 200 else {}
                msg_id = data.get("id", "latest")
                channel_id = data.get("channel_id", "channel")
                guild_id = data.get("guild_id", "@me")

                post_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{msg_id}"
                return self.success_result(posted_url=post_url)

        except httpx.TimeoutException:
            return self.failure_result("Discord API request timed out after 15 seconds.")
        except httpx.RequestError as exc:
            return self.failure_result(f"Network error communicating with Discord: {str(exc)}")
        except Exception as exc:
            return self.failure_result(f"Unexpected error posting to Discord: {str(exc)}")

    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        mock_id = 100000000000000000 + (uuid.uuid4().int % 900000000000000000)
        return self.success_result(
            posted_url=f"https://discord.com/channels/123456789/987654321/mock-{mock_id}",
            is_mock=True,
        )
