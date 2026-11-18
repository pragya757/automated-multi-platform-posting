"""
Telegram Bot integration for broadcasting messages to channels and groups.
Official API: Telegram Bot API (POST /bot<token>/sendMessage)
Documentation: https://core.telegram.org/bots/api#sendmessage
"""

import uuid
import httpx
from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class TelegramPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Telegram"

    @property
    def is_public(self) -> bool:
        return True

    def is_configured(self) -> bool:
        return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)

    async def post(self, message: str, cta_url: str) -> PlatformResult:
        """
        Publishes a message to a Telegram channel or group using official Bot API.
        """
        if not self.is_configured():
            return self.failure_result(
                "Missing credentials: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment."
            )

        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                response = await client.post(
                    api_url,
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "disable_web_page_preview": False,
                    },
                )

                data = response.json()
                if not data.get("ok"):
                    err_desc = data.get("description", "Unknown Telegram error")
                    return self.failure_result(f"Telegram API error ({response.status_code}): {err_desc}")

                result = data.get("result", {})
                message_id = result.get("message_id")
                chat_info = result.get("chat", {})
                username = chat_info.get("username")

                # Generate public link
                if username:
                    public_url = f"https://t.me/{username}/{message_id}"
                elif str(chat_id).startswith("@"):
                    clean_name = str(chat_id).lstrip("@")
                    public_url = f"https://t.me/{clean_name}/{message_id}"
                else:
                    # For private or ID-based channels
                    raw_id = str(chat_id).replace("-100", "").replace("-", "")
                    public_url = f"https://t.me/c/{raw_id}/{message_id}"

                return self.success_result(posted_url=public_url)

        except httpx.TimeoutException:
            return self.failure_result("Telegram API request timed out after 15 seconds.")
        except httpx.RequestError as exc:
            return self.failure_result(f"Network error communicating with Telegram: {str(exc)}")
        except Exception as exc:
            return self.failure_result(f"Unexpected error posting to Telegram: {str(exc)}")

    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        channel = settings.TELEGRAM_CHAT_ID.lstrip("@") if settings.TELEGRAM_CHAT_ID else "demochannel"
        mock_msg_id = 1000 + (uuid.uuid4().int % 9000)
        return self.success_result(
            posted_url=f"https://t.me/{channel}/mock-{mock_msg_id}",
            is_mock=True,
        )
