"""
Pydantic schemas for request validation and response formatting.
"""

from datetime import date as dt_date, time as dt_time
import re
from typing import List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator


# Regular expression to locate web URLs (http/https) in text
URL_REGEX = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


class PostingRequest(BaseModel):
    message: str = Field(
        ...,
        description="The message to post across platforms. Must not exceed 200 characters and must contain exactly one valid CTA URL.",
        examples=["Check out our latest business platform and grow your online visibility. https://example.com"],
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        # Strip whitespace for length and empty check
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message cannot be empty.")

        if len(trimmed) > 200:
            raise ValueError(
                f"Message must not exceed 200 characters. Current length: {len(trimmed)} characters."
            )

        # Detect URLs in message
        found_urls = URL_REGEX.findall(trimmed)
        if len(found_urls) == 0:
            raise ValueError(
                "Message must include exactly one Call-To-Action (CTA) URL starting with http:// or https://. Found 0."
            )
        if len(found_urls) > 1:
            raise ValueError(
                f"Message must include exactly one Call-To-Action (CTA) URL. Found {len(found_urls)} URLs: {', '.join(found_urls)}."
            )

        cta_url = found_urls[0].rstrip(".,;!?)")
        # Validate URL structure
        parsed = urlparse(cta_url)
        if parsed.scheme.lower() not in ("http", "https"):
            raise ValueError(f"CTA URL must have http or https scheme. Got: '{parsed.scheme}'.")
        if not parsed.netloc:
            raise ValueError(f"CTA URL '{cta_url}' does not have a valid host/domain name.")

        # Basic domain validation (must contain a dot or be localhost)
        host = parsed.netloc.split(":")[0]
        if host.lower() != "localhost" and "." not in host:
            raise ValueError(f"CTA URL '{cta_url}' has an invalid domain name: '{host}'.")

        return trimmed

    @property
    def cta_url(self) -> str:
        """Extract the validated CTA URL from the message."""
        found = URL_REGEX.findall(self.message)
        return found[0].rstrip(".,;!?)") if found else ""


class PlatformResult(BaseModel):
    platform: str = Field(..., description="Platform name")
    status: str = Field(..., description="'success' or 'failed'")
    posted_url: Optional[str] = Field(None, description="Direct published content URL")
    public_access: bool = Field(..., description="Whether content is publicly accessible on the web without logging in")
    date: Optional[str] = Field(None, description="Posting date (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Posting time (HH:MM:SS)")
    error: Optional[str] = Field(None, description="Error details if posting failed")


class PostingResponse(BaseModel):
    success: bool = Field(..., description="Overall status indicating if posting succeeded across any platform")
    results: List[PlatformResult] = Field(..., description="Individual platform posting results")
