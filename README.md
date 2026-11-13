# KARTZPIN DOWNLOADER — Backend starter

This is a FastAPI backend starter for the KARTZPIN DOWNLOADER frontend.

## Included
- `GET /` — service information
- `GET /api/health` — health check
- `POST /api/resolve` — validated Pinterest URL integration point
- CORS configured for the GitHub Pages origin
- Render deployment configuration

## Important
The `/api/resolve` endpoint intentionally returns HTTP 501 until an official or otherwise authorized content provider is integrated. This starter does not scrape Pinterest, bypass login/private-content restrictions, or fetch copyrighted media without permission.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to inspect the API.

## Deploy
1. Upload these files to a NEW GitHub repository named `kartzpin-backend`.
2. Connect that repository to a Python hosting provider such as Render.
3. The included `render.yaml` provides the build and start commands.
4. After deployment, test `/api/health`.
5. Set the real backend URL in the frontend JavaScript only after deployment is successful.

Do not put API keys or secrets in GitHub files.
