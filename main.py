import os
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, field_validator

APP_VERSION = "1.0.0"

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
        host = (urlparse(str(value)).hostname or "").lower()
        allowed = {"pinterest.com", "www.pinterest.com", "pin.it"}
        if host not in allowed:
            raise ValueError("Please enter a Pinterest pin URL.")
        if urlparse(str(value)).scheme != "https":
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
