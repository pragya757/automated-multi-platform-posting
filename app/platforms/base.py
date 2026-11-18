"""
Abstract Base Platform Class for all social/publishing platform integrations.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from app.schemas import PlatformResult


class BasePlatform(ABC):
    """
    Base class that every platform integration must implement.
    Ensures consistent interface, error handling, and reporting.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable platform name."""
        pass

    @property
    @abstractmethod
    def is_public(self) -> bool:
        """Whether posts on this platform are publicly viewable by anyone without an account."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if all required environment credentials for this platform are present."""
        pass

    @abstractmethod
    async def post(self, message: str, cta_url: str) -> PlatformResult:
        """
        Execute actual publishing to the platform's official API.
        Must handle its own exceptions and return a PlatformResult.
        """
        pass

    @abstractmethod
    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        """
        Execute a simulated/mock publishing run for testing.
        Clearly distinguished from actual live publishing.
        """
        pass

    def _now(self):
        """Helper to get current ISO date and time."""
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    def success_result(self, posted_url: str) -> PlatformResult:
        d, t = self._now()
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=self.is_public,
            date=d,
            time=t,
            error=None,
        )

    def failure_result(self, error_message: str) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="failed",
            posted_url=None,
            public_access=self.is_public,
            date=None,
            time=None,
            error=error_message,
        )
