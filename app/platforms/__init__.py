"""
Platform registry and exports.
"""

from app.platforms.base import BasePlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.reddit import RedditPlatform

ALL_PLATFORMS = [
    BlueskyPlatform,
    MastodonPlatform,
    TelegramPlatform,
    DiscordPlatform,
    RedditPlatform,
]

__all__ = [
    "BasePlatform",
    "BlueskyPlatform",
    "MastodonPlatform",
    "TelegramPlatform",
    "DiscordPlatform",
    "RedditPlatform",
    "ALL_PLATFORMS",
]
