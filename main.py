import os
import time
from collections import defaultdict, deque
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, field_validator

APP_VERSION = "1.0.0"

# Basic per-process protection for the single-instance starter deployment.
# For multiple Render instances, replace this with a shared store (for example Redis).
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60
MAX_RESOLVE_BODY_BYTES = 16 * 1024


class ResolveProtectionMiddleware:
    """Protect only POST /api/resolve; leave health checks unaffected."""

    def __init__(self, app):
        self.app = app
        self.requests_by_ip = defaultdict(deque)
        self.last_cleanup = 0.0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("path") != "/api/resolve" or scope.get("method") != "POST":
            await self.app(scope, receive, send)
            return

        # Use the ASGI client address. Do not trust a caller-supplied X-Forwarded-For header.
        client = scope.get("client")
        client_ip = client[0] if client and client[0] else "unknown"

        now = time.monotonic()
        bucket = self.requests_by_ip[client_ip]
        cutoff = now - RATE_LIMIT_WINDOW_SECONDS
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        if len(bucket) >= RATE_LIMIT_REQUESTS:
            await self._respond(send, 429, b'{"detail":"Too many requests. Please try again in a minute."}',
                                [(b"retry-after", b"60"), (b"content-type", b"application/json")])
            return

        bucket.append(now)

        # Periodically discard inactive IP buckets to keep memory bounded.
        if now - self.last_cleanup > RATE_LIMIT_WINDOW_SECONDS:
            stale_before = now - RATE_LIMIT_WINDOW_SECONDS
            stale_ips = [ip for ip, times in self.requests_by_ip.items()
                         if not times or times[-1] <= stale_before]
            for ip in stale_ips:
                self.requests_by_ip.pop(ip, None)
            self.last_cleanup = now

        # Reject oversized declared bodies before reading them.
        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                declared_size = int(content_length)
            except ValueError:
                await self._respond(send, 400, b'{"detail":"Invalid Content-Length header."}',
                                    [(b"content-type", b"application/json")])
                return
            if declared_size < 0 or declared_size > MAX_RESOLVE_BODY_BYTES:
                await self._respond(send, 413, b'{"detail":"Request body is too large."}',
                                    [(b"content-type", b"application/json")])
                return

        # Enforce the same limit even if Content-Length is absent or inaccurate.
        body_parts = []
        total_size = 0
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            part = message.get("body", b"")
            total_size += len(part)
            if total_size > MAX_RESOLVE_BODY_BYTES:
                # Drain the remaining request body, then return a controlled 413.
                while message.get("more_body", False):
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                await self._respond(send, 413, b'{"detail":"Request body is too large."}',
                                    [(b"content-type", b"application/json")])
                return
            body_parts.append(part)
            more_body = message.get("more_body", False)

        body = b"".join(body_parts)
        sent = False

        async def replay_body():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        await self.app(scope, replay_body, send)

    @staticmethod
    async def _respond(send, status, body, headers):
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": headers,
        })
        await send({
            "type": "http.response.body",
            "body": body,
            "more_body": False,
        })


app = FastAPI(
    title="KARTZPIN DOWNLOADER API",
    description="Backend starter for processing content the user owns or is authorized to download.",
    version=APP_VERSION,
)

origins = [
    item.strip()
    for item in os.getenv(
        "FRONTEND_ORIGINS",
        "https://thekartz48-glitch.github.io"
    ).split(",")
    if item.strip()
]

app.add_middleware(ResolveProtectionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ResolveRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def only_public_pinterest_urls(cls, value):
        parsed = urlparse(str(value))
        host = (parsed.hostname or "").lower()
        allowed = {"pinterest.com", "www.pinterest.com", "pin.it"}
        if host not in allowed:
            raise ValueError("Please enter a Pinterest pin URL.")
        if parsed.scheme != "https":
            raise ValueError("Only HTTPS links are accepted.")
        return value


@app.get("/")
def root():
    return {
        "service": "KARTZPIN DOWNLOADER API",
        "status": "online",
        "version": APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "kartzpin-backend"}


@app.post("/api/resolve")
def resolve_pin(payload: ResolveRequest):
    # Safe integration point:
    # Connect an official/authorized content provider here.
    # Do not scrape private content, bypass access controls, or
    # download content without the rights/permission to do so.
    raise HTTPException(
        status_code=501,
        detail=(
            "Pinterest content processing is not connected yet. "
            "A permitted, authorized provider/API must be configured first."
        ),
    )
