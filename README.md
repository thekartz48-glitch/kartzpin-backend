
# KARTZPIN DOWNLOADER — Backend

Python FastAPI backend for KARTZPIN DOWNLOADER.

## About

KARTZPIN DOWNLOADER is a backend starter project designed to support processing publicly accessible Pinterest content that the user owns or has permission to download.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- Pydantic

## Features

- FastAPI application
- API health check
- Pinterest URL validation
- HTTPS-only URL validation
- CORS configuration
- API documentation
- Authorized content processing integration point

## API Endpoints

### 1. Home

GET /

Returns backend service information.

### 2. Health Check

GET /api/health

Checks whether the backend is running.

### 3. Resolve Pinterest URL

POST /api/resolve

Accepts a Pinterest URL.

Note: Content processing is not connected yet. An authorized provider or official API must be configured before downloading is supported.

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_FOLDER
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn main:app --reload
```

Open API documentation:

http://127.0.0.1:8000/docs

## Environment Variables

FRONTEND_ORIGINS

Set this variable to your frontend website origin.

Default:

https://thekartz48-glitch.github.io

## Deployment

This project includes a render.yaml configuration for deployment on Render.

## Responsible Use

- Only process content you own or are authorized to download.
- Do not access private Pinterest content.
- Do not bypass authentication or access controls.
- Respect copyright and platform terms.

## Project

KARTZPIN DOWNLOADER

Backend Version: 1.0.0
