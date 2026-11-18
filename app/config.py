"""
Configuration settings loaded from environment variables (.env).
"""

import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class Settings:
    # Server settings
    HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("SERVER_PORT", "4000"))

    # Mock mode flag: when True, mock integrations are used for testing
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").strip().lower() in ("true", "1", "yes")

    # 1. Bluesky
    BLUESKY_HANDLE: str = os.getenv("BLUESKY_HANDLE", "").strip()
    BLUESKY_APP_PASSWORD: str = os.getenv("BLUESKY_APP_PASSWORD", "").strip()
    BLUESKY_PDS_URL: str = os.getenv("BLUESKY_PDS_URL", "https://bsky.social").strip()

    # 2. Mastodon
    MASTODON_INSTANCE_URL: str = os.getenv("MASTODON_INSTANCE_URL", "https://mastodon.social").strip().rstrip("/")
    MASTODON_ACCESS_TOKEN: str = os.getenv("MASTODON_ACCESS_TOKEN", "").strip()

    # 3. Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    # 4. Discord
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

    # 5. Reddit
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "").strip()
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    REDDIT_USERNAME: str = os.getenv("REDDIT_USERNAME", "").strip()
    REDDIT_PASSWORD: str = os.getenv("REDDIT_PASSWORD", "").strip()
    REDDIT_SUBREDDIT: str = os.getenv("REDDIT_SUBREDDIT", "test").strip()


settings = Settings()
