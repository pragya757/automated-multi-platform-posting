"""
Bluesky (AT Protocol) integration for publishing text posts with link facets.
Official API: AT Protocol XRPC (com.atproto.server.createSession & com.atproto.repo.createRecord)
Documentation: https://docs.bsky.app
"""

from datetime import datetime, timezone
import uuid
import httpx
from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class BlueskyPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Bluesky"

    @property
    def is_public(self) -> bool:
        return True

    def is_configured(self) -> bool:
        return bool(settings.BLUESKY_HANDLE and settings.BLUESKY_APP_PASSWORD)

    async def post(self, message: str, cta_url: str) -> PlatformResult:
        """
        Publishes a post to Bluesky using AT Protocol XRPC endpoints.
        """
        if not self.is_configured():
            return self.failure_result(
                "Missing credentials: Set BLUESKY_HANDLE and BLUESKY_APP_PASSWORD in environment."
            )

        pds_url = settings.BLUESKY_PDS_URL.rstrip("/")
        handle = settings.BLUESKY_HANDLE
        app_password = settings.BLUESKY_APP_PASSWORD

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # 1. Authenticate with AT Protocol PDS to create a session
                session_resp = await client.post(
                    f"{pds_url}/xrpc/com.atproto.server.createSession",
                    json={"identifier": handle, "password": app_password},
                )

                if session_resp.status_code != 200:
                    err_msg = session_resp.json().get("message", session_resp.text)
                    return self.failure_result(f"Bluesky auth error ({session_resp.status_code}): {err_msg}")

                session_data = session_resp.json()
                access_jwt = session_data["accessJwt"]
                repo_did = session_data["did"]

                # 2. Build link facet with UTF-8 byte offsets as required by AT Protocol
                facets = []
                msg_bytes = message.encode("utf-8")
                url_bytes = cta_url.encode("utf-8")
                byte_start = msg_bytes.find(url_bytes)
                if byte_start != -1:
                    byte_end = byte_start + len(url_bytes)
                    facets.append({
                        "index": {
                            "byteStart": byte_start,
                            "byteEnd": byte_end,
                        },
                        "features": [{
                            "$type": "app.bsky.richtext.facet#link",
                            "uri": cta_url,
                        }],
                    })

                # 3. Create Record (app.bsky.feed.post)
                now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                record_payload = {
                    "repo": repo_did,
                    "collection": "app.bsky.feed.post",
                    "record": {
                        "$type": "app.bsky.feed.post",
                        "text": message,
                        "createdAt": now_iso,
                        "facets": facets,
                    },
                }

                post_resp = await client.post(
                    f"{pds_url}/xrpc/com.atproto.repo.createRecord",
                    headers={"Authorization": f"Bearer {access_jwt}"},
                    json=record_payload,
                )

                if post_resp.status_code not in (200, 201):
                    err_msg = post_resp.json().get("message", post_resp.text)
                    return self.failure_result(f"Bluesky post error ({post_resp.status_code}): {err_msg}")

                post_data = post_resp.json()
                # URI format: at://did:plc:.../app.bsky.feed.post/{rkey}
                uri = post_data.get("uri", "")
                rkey = uri.split("/")[-1] if uri else "latest"
                public_url = f"https://bsky.app/profile/{handle}/post/{rkey}"

                return self.success_result(posted_url=public_url)

        except httpx.TimeoutException:
            return self.failure_result("Bluesky API request timed out after 15 seconds.")
        except httpx.RequestError as exc:
            return self.failure_result(f"Network error communicating with Bluesky: {str(exc)}")
        except Exception as exc:
            return self.failure_result(f"Unexpected error posting to Bluesky: {str(exc)}")

    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        handle = settings.BLUESKY_HANDLE or "demo-user.bsky.social"
        mock_rkey = uuid.uuid4().hex[:12]
        return self.success_result(posted_url=f"https://bsky.app/profile/{handle}/post/mock-{mock_rkey}")
