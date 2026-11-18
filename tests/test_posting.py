"""
Comprehensive unit and integration test suite for the Automated Multi-Platform Posting System.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostingRequest
from app.services.posting_service import PostingService


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ------------------------------------------------------------------------------
# 1. Input Validation Tests
# ------------------------------------------------------------------------------

def test_valid_message_validation():
    valid_text = "Check out our latest business platform and grow your online visibility. https://example.com"
    req = PostingRequest(message=valid_text)
    assert req.message == valid_text
    assert req.cta_url == "https://example.com"


def test_validation_fails_when_message_exceeds_200_chars():
    long_message = "A" * 180 + " https://example.com"  # 180 + 20 = 200 chars
    assert len(long_message) == 200
    # Exactly 200 chars should pass
    req = PostingRequest(message=long_message)
    assert len(req.message) == 200

    # 201 chars should fail
    too_long = "A" * 181 + " https://example.com"
    with pytest.raises(ValueError, match="must not exceed 200 characters"):
        PostingRequest(message=too_long)


def test_validation_fails_without_url():
    no_url = "Check out our latest business platform and grow your visibility."
    with pytest.raises(ValueError, match="must include exactly one Call-To-Action"):
        PostingRequest(message=no_url)


def test_validation_fails_with_multiple_urls():
    two_urls = "Visit https://first.com and also see https://second.com for details."
    with pytest.raises(ValueError, match="Found 2 URLs"):
        PostingRequest(message=two_urls)


def test_validation_fails_with_empty_or_whitespace():
    with pytest.raises(ValueError, match="cannot be empty"):
        PostingRequest(message="   ")


def test_validation_fails_with_invalid_url_scheme():
    invalid_scheme = "Check out our files ftp://files.example.com/doc"
    with pytest.raises(ValueError, match="must include exactly one Call-To-Action"):
        PostingRequest(message=invalid_scheme)


def test_validation_fails_with_malformed_url():
    malformed = "Visit this site https://-invalid"
    with pytest.raises(ValueError, match="invalid domain name"):
        PostingRequest(message=malformed)


# ------------------------------------------------------------------------------
# 2. API Endpoint Integration Tests (using HTTPX AsyncClient)
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_api_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "operational"
        assert len(data["supported_platforms"]) == 5
        assert "Bluesky" in data["supported_platforms"]
        assert "Mastodon" in data["supported_platforms"]
        assert "Telegram" in data["supported_platforms"]
        assert "Discord" in data["supported_platforms"]
        assert "Reddit" in data["supported_platforms"]


@pytest.mark.asyncio
async def test_api_platforms_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/platforms")
        assert resp.status_code == 200
        data = resp.json()
        platforms = data["platforms"]
        assert len(platforms) == 5
        names = [p["name"] for p in platforms]
        assert "Bluesky" in names
        assert "Discord" in names
        # Discord is login-gated
        discord = next(p for p in platforms if p["name"] == "Discord")
        assert discord["public_access"] is False
        # Bluesky is publicly accessible
        bluesky = next(p for p in platforms if p["name"] == "Bluesky")
        assert bluesky["public_access"] is True


@pytest.mark.asyncio
async def test_api_posting_validation_error_returned():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Missing CTA URL
        resp = await client.post("/posting", json={"message": "No link message here"})
        assert resp.status_code == 422
        assert "Call-To-Action" in resp.text


@pytest.mark.asyncio
async def test_api_posting_mock_success_all_platforms():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Check out our latest business platform and grow your online visibility. https://example.com"
        }
        resp = await client.post("/posting?mock=true", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["success"] is True
        assert data["mock_mode"] is True
        assert len(data["results"]) == 5

        for item in data["results"]:
            assert item["status"] == "success"
            assert item["is_mock"] is True
            assert item["posted_url"] is not None
            assert item["date"] is not None
            assert item["time"] is not None
            assert item["error"] is None
            assert isinstance(item["public_access"], bool)


@pytest.mark.asyncio
async def test_api_posting_without_credentials_fails_gracefully():
    """When credentials are not supplied and mock is False, platforms return failed status with clear error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Check out our latest business platform and grow your online visibility. https://example.com"
        }
        resp = await client.post("/posting?mock=false", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        for item in data["results"]:
            # Unless real environment credentials were supplied in the host system,
            # each unconfigured platform reports failure gracefully
            if item["status"] == "failed":
                assert item["posted_url"] is None
                assert item["public_access"] is False
                assert item["date"] is None
                assert item["time"] is None
                assert item["is_mock"] is False
                assert item["error"] is not None
                assert "credentials" in item["error"].lower()


# ------------------------------------------------------------------------------
# 3. Independent Error Handling Unit Tests
# ------------------------------------------------------------------------------

class SuccessfulDummyPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Dummy Success"

    @property
    def is_public(self) -> bool:
        return True

    def is_configured(self) -> bool:
        return True

    async def post(self, message: str, cta_url: str) -> PlatformResult:
        return self.success_result(posted_url="https://success.example.com/1")

    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        return self.success_result(posted_url="https://mock.example.com/1")


class FailingDummyPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Dummy Failure"

    @property
    def is_public(self) -> bool:
        return False

    def is_configured(self) -> bool:
        return True

    async def post(self, message: str, cta_url: str) -> PlatformResult:
        raise ConnectionResetError("Connection abruptly terminated by peer")

    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        return self.failure_result("Simulated failure")


@pytest.mark.asyncio
async def test_independent_error_handling_isolation():
    """Verify that a catastrophic failure on one platform does not impact another platform."""
    service = PostingService(platforms=[SuccessfulDummyPlatform(), FailingDummyPlatform()])

    response = await service.publish_to_all(
        message="Test message https://example.com",
        cta_url="https://example.com",
        force_mock=False,
    )

    assert response.success is True
    assert len(response.results) == 2

    success_item = next(r for r in response.results if r.platform == "Dummy Success")
    assert success_item.status == "success"
    assert success_item.posted_url == "https://success.example.com/1"
    assert success_item.error is None

    failure_item = next(r for r in response.results if r.platform == "Dummy Failure")
    assert failure_item.status == "failed"
    assert failure_item.posted_url is None
    assert "Connection abruptly terminated" in failure_item.error


# ------------------------------------------------------------------------------
# 4. Detailed Validation API Rejection Tests
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_api_posting_exactly_200_chars_accepted():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Message with exactly 200 characters
        exact_200_msg = "X" * 180 + " https://example.com"
        assert len(exact_200_msg) == 200

        resp = await client.post("/posting?mock=true", json={"message": exact_200_msg})
        assert resp.status_code == 200
        assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_api_posting_exceeding_200_chars_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        too_long = "X" * 181 + " https://example.com"
        assert len(too_long) == 201

        resp = await client.post("/posting?mock=true", json={"message": too_long})
        assert resp.status_code == 422
        assert "must not exceed 200 characters" in resp.text


@pytest.mark.asyncio
async def test_api_posting_multiple_urls_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        multi = "Check https://site1.com and https://site2.com for details."
        resp = await client.post("/posting?mock=true", json={"message": multi})
        assert resp.status_code == 422
        assert "exactly one Call-To-Action" in resp.text


@pytest.mark.asyncio
async def test_api_posting_malformed_url_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bad_url = "Visit https://invalid-host-without-dot for news."
        resp = await client.post("/posting?mock=true", json={"message": bad_url})
        assert resp.status_code == 422
        assert "invalid domain name" in resp.text

