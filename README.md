# Automated Multi-Platform Posting System

A high-performance, asynchronous REST API service built with **FastAPI**, **Pydantic v2**, and **HTTPX** that automatically publishes short promotional and marketing messages across multiple third-party social and broadcasting platforms through their official APIs.

---

## 🌐 Live Production Deployment

The application is deployed live on **Vercel** serverless infrastructure:

| Resource | URL |
| :--- | :--- |
| **Live Production Base URL** | [https://automated-multi-platform-posting-six.vercel.app](https://automated-multi-platform-posting-six.vercel.app) |
| **Interactive API Documentation (Swagger UI)** | [https://automated-multi-platform-posting-six.vercel.app/docs](https://automated-multi-platform-posting-six.vercel.app/docs) |
| **ReDoc API Documentation** | [https://automated-multi-platform-posting-six.vercel.app/redoc](https://automated-multi-platform-posting-six.vercel.app/redoc) |
| **OpenAPI 3.1 Specification (JSON)** | [https://automated-multi-platform-posting-six.vercel.app/openapi.json](https://automated-multi-platform-posting-six.vercel.app/openapi.json) |
| **Supported Platforms Status** | [https://automated-multi-platform-posting-six.vercel.app/platforms](https://automated-multi-platform-posting-six.vercel.app/platforms) |
| **Public GitHub Repository** | [https://github.com/pragya757/automated-multi-platform-posting](https://github.com/pragya757/automated-multi-platform-posting) |

---

## 1. Executive Summary & Platform Research

To meet the requirement of publishing short messages ($\le 200$ characters containing exactly one Call-To-Action link) across multiple third-party platforms with **accessible, free/low-cost official developer APIs**, the following 5 platforms were evaluated, selected, and integrated:

| Platform | Official API Type | Cost Tier | Developer Registration Difficulty | Public Web Access | Character Limit | Key Developer Benefit |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Bluesky** | AT Protocol XRPC | Free | Instant (App Password) | **Yes** | 300 | Open protocol, no waiting or app approval needed |
| **Mastodon** | ActivityPub / REST v1 | Free | Instant (User Settings) | **Yes** | 500 | Self-service Bearer token generated in 30 seconds |
| **Telegram** | Telegram Bot API | Free | Instant via `@BotFather` | **Yes** | 4,096 | Zero approval process; public channel links |
| **Discord** | Webhook / REST v10 | Free | Instant (Server Settings) | **No** (Login-gated) | 2,000 | Instant webhook URL without app verification |
| **Reddit** | OAuth2 REST API | Free | Instant (Script App) | **Yes** | 40,000 | Official script application with client credentials |

---

## 2. Official Developer Portals & Registration Guide

Follow these guides to acquire official API credentials for each platform without fabricating keys:

### 1. Bluesky (AT Protocol)
* **Portal / Documentation:** [https://docs.bsky.app](https://docs.bsky.app)
* **Registration Steps:**
  1. Create or log into your account at [https://bsky.app](https://bsky.app).
  2. Navigate to **Settings** $\rightarrow$ **Privacy and Security** $\rightarrow$ **App Passwords**.
  3. Click **Add App Password**, enter a name (e.g., `FastAPIPoster`), and click **Create App Password**.
  4. Copy the generated password.
  5. Add to `.env`:
     ```bash
     BLUESKY_HANDLE=your_handle.bsky.social
     BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
     BLUESKY_PDS_URL=https://bsky.social
     ```

### 2. Mastodon
* **Portal / Documentation:** [https://docs.joinmastodon.org/client/intro/](https://docs.joinmastodon.org/client/intro/)
* **Registration Steps:**
  1. Register on any Mastodon instance (e.g., [https://mastodon.social](https://mastodon.social)).
  2. Go to **Preferences** $\rightarrow$ **Development** $\rightarrow$ **New Application**.
  3. Enter application name (e.g., `FastAPI Multi-Poster`), grant write permissions (`write:statuses`), and submit.
  4. Copy the generated **Access Token**.
  5. Add to `.env`:
     ```bash
     MASTODON_INSTANCE_URL=https://mastodon.social
     MASTODON_ACCESS_TOKEN=your_access_token
     ```

### 3. Telegram
* **Portal / Documentation:** [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)
* **Registration Steps:**
  1. Open Telegram and search for `@BotFather` ([https://t.me/BotFather](https://t.me/BotFather)).
  2. Send `/newbot`, name your bot, and choose a unique username ending in `bot`.
  3. Copy the HTTP API token provided by BotFather.
  4. Create a public Telegram channel, add your bot to the channel, and promote it to **Administrator** (with "Post Messages" permission).
  5. Add to `.env`:
     ```bash
     TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
     TELEGRAM_CHAT_ID=@your_public_channel_name
     ```

### 4. Discord
* **Portal / Documentation:** [https://discord.com/developers/docs/resources/webhook](https://discord.com/developers/docs/resources/webhook)
* **Registration Steps:**
  1. Open Discord and go to your server (or create a free personal server).
  2. Right-click the destination channel $\rightarrow$ **Edit Channel** $\rightarrow$ **Integrations** $\rightarrow$ **Webhooks**.
  3. Click **New Webhook**, name it (e.g., `Marketing Announcer`), and click **Copy Webhook URL**.
  4. Add to `.env`:
     ```bash
     DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/token_here
     ```

### 5. Reddit
* **Portal / Documentation:** [https://www.reddit.com/dev/api/](https://www.reddit.com/dev/api/)
* **Registration Steps:**
  1. Log into Reddit and open [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
  2. Scroll down and click **create another app...** (or **create app**).
  3. Select the **script** radio button (intended for personal scripts/bots).
  4. Enter name (e.g., `multi-platform-poster`), redirect URI (`http://localhost:8080`), and create.
  5. The string beneath the app name is the `REDDIT_CLIENT_ID`; the `secret` is `REDDIT_CLIENT_SECRET`.
  6. Add to `.env`:
     ```bash
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     REDDIT_USERNAME=your_reddit_username
     REDDIT_PASSWORD=your_reddit_password
     REDDIT_SUBREDDIT=test
     ```

---

## 3. Architecture & Key Features

```text
practical-test-main-pragya/
├── app/
│   ├── config.py                 # Pydantic/dotenv configuration management
│   ├── schemas.py                # Pydantic v2 validation models
│   ├── main.py                   # FastAPI application and routing
│   ├── platforms/
│   │   ├── base.py               # Abstract BasePlatform class
│   │   ├── bluesky.py            # Bluesky AT Protocol XRPC implementation
│   │   ├── mastodon.py           # Mastodon REST API v1 implementation
│   │   ├── telegram.py           # Telegram Bot API implementation
│   │   ├── discord.py            # Discord Webhook execution implementation
│   │   └── reddit.py             # Reddit OAuth2 script implementation
│   └── services/
│       └── posting_service.py    # Concurrency and failure-isolation orchestrator
├── tests/
│   └── test_posting.py           # 13 automated unit & integration tests
├── .env.example                  # Template with credential descriptions
├── requirements.txt              # Production dependencies
├── pytest.ini                    # Test suite configuration
└── README.md
```

### Key Technical Characteristics:
1. **Pydantic Validation**:
   - Enforces maximum length of **200 characters**.
   - Enforces **exactly one Call-To-Action (CTA) URL** with `http` or `https` scheme.
   - Rejects messages with 0 URLs, $> 1$ URLs, invalid domain names, or excessive length.
2. **Independent Error Handling & Isolation**:
   - Platforms run concurrently using `asyncio.gather`.
   - Each platform handles exceptions individually. If one platform fails (e.g. rate limit, bad token, timeout), all other platforms continue publishing normally.
3. **Mock Mode vs. Live Publishing**:
   - When credentials are not yet supplied or during automated testing, **Mock Mode** (`MOCK_MODE=true` in `.env` or `POST /posting?mock=true`) generates realistic, clearly distinguished mock responses.
   - When live credentials are provided in `.env`, the system posts to real official APIs and returns the actual live published URLs.

---

## 4. Setup and Installation

### Prerequisites
* Python 3.10+ (tested with Python 3.14)
* Virtual environment (`venv`)

### 1. Clone & Set Up Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
Open `.env` and enter your credentials. If you want to run purely in mock mode for testing without credentials:
```bash
MOCK_MODE=true
```

### 3. Run the Local Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

Interactive Swagger documentation is available at:
**[http://localhost:4000/docs](http://localhost:4000/docs)**

---

## 5. API Reference

### `POST /posting`
Publishes a validated text message with one CTA URL across all platforms.

#### Request Headers
`Content-Type: application/json`

#### Request Query Parameters (Optional)
* `mock` (boolean, optional): Set to `true` to force mock mode for testing without altering `.env`.

#### Request Body
```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

#### Production Test cURL Command
```bash
curl -X POST "https://automated-multi-platform-posting-six.vercel.app/posting?mock=true" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our latest business platform and grow your online visibility. https://example.com"}'
```

#### Sample Successful Response (200 OK - Mock Simulation Mode)
```json
{
  "success": true,
  "mock_mode": true,
  "results": [
    {
      "platform": "Bluesky",
      "status": "success",
      "posted_url": "https://bsky.app/profile/demo-user.bsky.social/post/mock-2d7fdcb1826c",
      "public_access": true,
      "date": "2026-11-18",
      "time": "15:00:07",
      "error": null,
      "is_mock": true
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@demouser/mock-5fdb6ca388",
      "public_access": true,
      "date": "2026-11-18",
      "time": "15:00:07",
      "error": null,
      "is_mock": true
    },
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/demochannel/mock-9743",
      "public_access": true,
      "date": "2026-11-18",
      "time": "15:00:07",
      "error": null,
      "is_mock": true
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://discord.com/channels/123456789/987654321/mock-384568053534899355",
      "public_access": false,
      "date": "2026-11-18",
      "time": "15:00:07",
      "error": null,
      "is_mock": true
    },
    {
      "platform": "Reddit",
      "status": "success",
      "posted_url": "https://www.reddit.com/r/test/comments/mock-8255bd9/",
      "public_access": true,
      "date": "2026-11-18",
      "time": "15:00:07",
      "error": null,
      "is_mock": true
    }
  ]
}
```

#### Sample Response Without Credentials (200 OK - Safe Failure Reporting)
When live posting is requested (`mock=false`) without `.env` credentials configured:
```json
{
  "success": false,
  "mock_mode": false,
  "results": [
    {
      "platform": "Bluesky",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Platform credentials not configured in environment variables. Configure .env or set MOCK_MODE=true for testing.",
      "is_mock": false
    }
  ]
}
```

#### Sample Validation Error (422 Unprocessable Entity)
When input has no URL:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must include exactly one Call-To-Action (CTA) URL starting with http:// or https://. Found 0.",
      "input": "Check out our latest business platform and grow your online visibility."
    }
  ]
}
```

When input exceeds 200 characters:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must not exceed 200 characters. Current length: 201 characters.",
      "input": "..."
    }
  ]
}
```

---

## 6. Running Tests

Run the complete automated test suite with pytest:

```bash
pytest -v
```

Output:
```text
============================= test session starts ==============================
platform darwin -- Python 3.14.4, pytest-9.2.0, pluggy-1.7.0
rootdir: /Users/pragya/Downloads/practical-test-main-pragya
configfile: pytest.ini
plugins: anyio-4.16.0, asyncio-1.5.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 17 items

tests/test_posting.py::test_valid_message_validation PASSED              [  5%]
tests/test_posting.py::test_validation_fails_when_message_exceeds_200_chars PASSED [ 11%]
tests/test_posting.py::test_validation_fails_without_url PASSED          [ 17%]
tests/test_posting.py::test_validation_fails_with_multiple_urls PASSED   [ 23%]
tests/test_posting.py::test_validation_fails_with_empty_or_whitespace PASSED [ 29%]
tests/test_posting.py::test_validation_fails_with_invalid_url_scheme PASSED [ 35%]
tests/test_posting.py::test_validation_fails_with_malformed_url PASSED   [ 41%]
tests/test_posting.py::test_api_root_endpoint PASSED                     [ 47%]
tests/test_posting.py::test_api_platforms_endpoint PASSED                [ 52%]
tests/test_posting.py::test_api_posting_validation_error_returned PASSED [ 58%]
tests/test_posting.py::test_api_posting_mock_success_all_platforms PASSED [ 64%]
tests/test_posting.py::test_api_posting_without_credentials_fails_gracefully PASSED [ 70%]
tests/test_posting.py::test_independent_error_handling_isolation PASSED  [ 76%]
tests/test_posting.py::test_api_posting_exactly_200_chars_accepted PASSED [ 82%]
tests/test_posting.py::test_api_posting_exceeding_200_chars_rejected PASSED [ 88%]
tests/test_posting.py::test_api_posting_multiple_urls_rejected PASSED    [ 94%]
tests/test_posting.py::test_api_posting_malformed_url_rejected PASSED    [100%]

============================== 17 passed in 0.15s ==============================
```
tests/test_posting.py::test_api_platforms_endpoint PASSED                [ 69%]
tests/test_posting.py::test_api_posting_validation_error_returned PASSED [ 76%]
tests/test_posting.py::test_api_posting_mock_success_all_platforms PASSED [ 84%]
tests/test_posting.py::test_api_posting_without_credentials_fails_gracefully PASSED [ 92%]
tests/test_posting.py::test_independent_error_handling_isolation PASSED  [100%]

============================== 13 passed in 0.10s ==============================
```

---

## 7. Submission Checklist Verification

- [x] **FastAPI & API Structure**: Modular architecture following clean code principles (`app/platforms/`, `app/services/`, `app/schemas.py`).
- [x] **Input Validation**: Length $\le 200$ characters and exactly 1 valid CTA URL strictly enforced with descriptive validation errors.
- [x] **Platform Research & Integration**: 5 independent integrations (Bluesky, Mastodon, Telegram, Discord, Reddit) using official endpoints.
- [x] **Multi-Platform Posting**: Concurrently triggered via `asyncio.gather`.
- [x] **Independent Error Handling**: Failure on one platform does not impact or stop any other platform.
- [x] **No Hardcoded Keys**: All credentials managed via `.env` and environment variables.
- [x] **Mock Mode for Reviewers**: Seamless testing via `MOCK_MODE=true` or query parameter `POST /posting?mock=true`.
