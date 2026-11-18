"""
Reddit API integration for submitting text posts to subreddits.
Official API: Reddit OAuth2 API (POST /api/v1/access_token & POST /api/submit)
Documentation: https://www.reddit.com/dev/api/
"""

import uuid
import httpx
from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class RedditPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Reddit"

    @property
    def is_public(self) -> bool:
        return True

    def is_configured(self) -> bool:
        return bool(
            settings.REDDIT_CLIENT_ID
            and settings.REDDIT_CLIENT_SECRET
            and settings.REDDIT_USERNAME
            and settings.REDDIT_PASSWORD
        )

    async def post(self, message: str, cta_url: str) -> PlatformResult:
        """
        Submits a text post to Reddit using official OAuth2 endpoints.
        """
        if not self.is_configured():
            return self.failure_result(
                "Missing credentials: Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, and REDDIT_PASSWORD."
            )

        client_id = settings.REDDIT_CLIENT_ID
        client_secret = settings.REDDIT_CLIENT_SECRET
        username = settings.REDDIT_USERNAME
        password = settings.REDDIT_PASSWORD
        subreddit = settings.REDDIT_SUBREDDIT or "test"
        user_agent = f"MultiPlatformPoster/1.0 (by /u/{username})"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # 1. Obtain OAuth2 access token via script application password flow
                auth_resp = await client.post(
                    "https://www.reddit.com/api/v1/access_token",
                    auth=(client_id, client_secret),
                    data={
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                    },
                    headers={"User-Agent": user_agent},
                )

                if auth_resp.status_code != 200:
                    return self.failure_result(
                        f"Reddit authentication failed ({auth_resp.status_code}): {auth_resp.text}"
                    )

                auth_data = auth_resp.json()
                access_token = auth_data.get("access_token")
                if not access_token:
                    err = auth_data.get("error", "Failed to retrieve access token")
                    return self.failure_result(f"Reddit auth error: {err}")

                # 2. Derive title from message (up to 80 chars)
                title = message[:80].strip()
                if len(message) > 80:
                    title += "..."

                # 3. Submit post to target subreddit
                submit_resp = await client.post(
                    "https://oauth.reddit.com/api/submit",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "User-Agent": user_agent,
                    },
                    data={
                        "sr": subreddit,
                        "kind": "self",
                        "title": title,
                        "text": message,
                        "resubmit": "true",
                    },
                )

                if submit_resp.status_code != 200:
                    return self.failure_result(
                        f"Reddit submit error ({submit_resp.status_code}): {submit_resp.text}"
                    )

                submit_data = submit_resp.json()
                json_body = submit_data.get("json", {})
                errors = json_body.get("errors", [])
                if errors:
                    err_desc = ", ".join(str(e) for e in errors)
                    return self.failure_result(f"Reddit rejection: {err_desc}")

                data_node = json_body.get("data", {})
                post_url = data_node.get("url")
                if not post_url:
                    post_url = f"https://www.reddit.com/r/{subreddit}/"

                return self.success_result(posted_url=post_url)

        except httpx.TimeoutException:
            return self.failure_result("Reddit API request timed out after 15 seconds.")
        except httpx.RequestError as exc:
            return self.failure_result(f"Network error communicating with Reddit: {str(exc)}")
        except Exception as exc:
            return self.failure_result(f"Unexpected error posting to Reddit: {str(exc)}")

    async def post_mock(self, message: str, cta_url: str) -> PlatformResult:
        sub = settings.REDDIT_SUBREDDIT or "test"
        mock_id = uuid.uuid4().hex[:7]
        return self.success_result(posted_url=f"https://www.reddit.com/r/{sub}/comments/mock-{mock_id}/")
