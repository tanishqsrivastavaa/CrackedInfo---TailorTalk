# CrackedInfo - TailorTalk Drive Search Assignment

Conversational Google Drive search assistant built for the TailorTalk internship assignment.

## Stack

- Backend API: FastAPI
- Agent/tooling: LangChain + Groq chat model
- Drive integration: Google Drive API (service account)
- Frontend test UI: Streamlit
- Package/runtime: `uv`

## Repository Layout

- `backend/app` - FastAPI app, agent flow, Drive services, query builder
- `backend/tests` - pytest test suite for query generation and search behavior
- `backend/streamlit_app.py` - basic Streamlit chat UI for testing `/chat`
- `secrets/` - local-only secret files (gitignored)

## Features Implemented

- Structured Drive search parameters (`DriveSearchParams`)
- Safe Google Drive `q` query builder with escaping
- Search by:
  - exact name (`name = ...`)
  - partial name (`name contains ...`)
  - full text (`fullText contains ...`)
  - MIME type/file aliases (pdf, docs, sheets/excel/xlsx, slides, folders, images/png, videos/mp4, shell script)
  - date filters (`modified_after`, `modified_before`)
- Natural language helpers for date intent (`today`, `yesterday`, `last week`, `before ...`, `after ...`)
- Default query scoping:
  - folder scope using `DRIVE_FOLDER_ID` (when set)
  - `trashed = false`
- Explicit Drive error propagation in API responses

## API

### Health

- `GET /`

### Chat Search

- `POST /chat`
- Request:

```json
{
  "message": "Find pdf reports from last week"
}
```

- Response shape:

```json
{
  "message": "Find pdf reports from last week",
  "assistant_answer": "Found 4 files.",
  "query": "'<folder-id>' in parents and trashed = false and mimeType = 'application/pdf' and modifiedTime > '2026-05-09T00:00:00Z'",
  "count": 4,
  "files": [],
  "error": null
}
```

## Environment Variables

Backend reads env from `backend/.env` locally and service env in deployment.

Required/used variables:

- `DATABASE_URL` - required by current settings model
- `APP_NAME` - app name
- `ENVIRONMENT` - e.g. `local`, `production`
- `GROQ_API_KEY` - Groq API key
- `DRIVE_FOLDER_ID` - Google Drive folder ID to scope search

Google credentials (choose one):

- `GOOGLE_SERVICE_ACCOUNT_JSON` - full JSON content (recommended for cloud, including Render)
- `SERVICE_SECRET` - local filesystem path to service account JSON file (local dev fallback)

## Local Setup

### 1) Install dependencies

From repo root:

```bash
uv sync
```

or backend-only:

```bash
cd backend
uv sync
```

### 2) Configure local env

Create `backend/.env` with values similar to:

```env
DATABASE_URL=sqlite:///./app.db
APP_NAME=CrackedInfo
ENVIRONMENT=local
GROQ_API_KEY=your_groq_key
DRIVE_FOLDER_ID=your_copied_drive_folder_id
SERVICE_SECRET=../secrets/your-service-account.json
# GOOGLE_SERVICE_ACCOUNT_JSON=optional_local_json_blob
```

### 3) Share Drive folder with service account

1. Copy assignment folder into your Drive.
2. Share copied folder with service account `client_email` as Viewer.
3. Set `DRIVE_FOLDER_ID` to that copied folder ID.

## Run Locally

### Backend

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Streamlit test UI

```bash
cd backend
uv run streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

In sidebar, set backend URL to:

- local: `http://127.0.0.1:8000/chat`
- deployed backend: `https://<your-backend>.onrender.com/chat`

## Tests

Run backend tests:

```bash
cd backend
uv run --with pytest pytest -q
```

Static compile check:

```bash
cd backend
uv run python -m compileall -q app tests
```

## Deployment

### Render (Backend)

- Root Directory: `backend`
- Build Command: `uv sync`
- Start Command:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set env vars in Render:

- `DATABASE_URL`
- `APP_NAME`
- `ENVIRONMENT`
- `GROQ_API_KEY`
- `DRIVE_FOLDER_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON blob)

Do not use local path-style `SERVICE_SECRET` on Render unless you also provision that file inside the container.

### Streamlit Cloud (Frontend test UI)

- Main file path: `backend/streamlit_app.py`
- Ensure `backend/pyproject.toml` includes proper Python range (`>=3.13,<4.0.0`).
- In app sidebar, set backend URL to deployed backend `/chat` endpoint.

## Troubleshooting

- `405 Method Not Allowed` from Streamlit:
  - You likely pointed to backend root `/` instead of `/chat`.
- `Connection refused` to `127.0.0.1` in cloud:
  - Cloud app cannot reach your local machine; use deployed backend URL.
- Drive returns empty/irrelevant results:
  - verify `DRIVE_FOLDER_ID` and folder sharing with service account.
- Drive auth errors:
  - verify `GOOGLE_SERVICE_ACCOUNT_JSON` is valid JSON and from correct project.

## Assignment Notes

- Streamlit UI here is a minimal test interface.
- Primary assignment requirement is robust conversational Drive search via backend agent/tool flow and accurate Drive query generation.
