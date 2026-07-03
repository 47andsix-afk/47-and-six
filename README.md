# 47-&-SIX Concierge

A private chef and catering platform with a FastAPI backend, Gemini AI orchestration, ChromaDB knowledge search, and static chef-themed frontend pages.

## Overview

This project is built around a single FastAPI entrypoint (`main.py`) that exposes:

- `/agents/*` for specialized agent workflows
- `/chat` for direct AI concierge interactions
- `/chef-dashboard`, `/menu-cost`, `/event-planning`, `/inventory` for operational support
- `/chef/credentials` and `/chef/knowledge/*` for internal profile and knowledge inspection
- `/embed` for embedding text into ChromaDB

The backend uses Google Gemini with optional mock fallback and supports local ChromaDB embedding storage.

## Architecture

- `main.py` — single FastAPI app, middleware, route definitions, and startup logic.
- `agents/` — modular agent implementations and a small RONIN task router.
- `chef_knowledge/` — index building, file loading, and knowledge router for chef training data.
- Static frontend pages (`index.html`, `dashboard.html`, etc.) plus shared `style.css` and `script.js`.

## Key Components

### Backend

- `FastAPI` for request routing
- `CORS` middleware enabled for local frontend access
- `google-genai` and `google-ai-generativelanguage` for Gemini generation and embeddings
- `chromadb` for local operational and chef knowledge vector search
- `python-dotenv` for environment configuration

### Frontend

- `script.js` provides API helper functions for agents and chef knowledge routes
- static HTML pages use shared navigation and theme styling

### Agent System

- `/agents/concierge` — fused concierge agent with contextual operational reasoning
- `/agents/ops`, `/agents/logistics`, `/agents/economics`, `/agents/compliance` — specialized agent endpoints
- `/agents/memory` — local context retrieval from ChromaDB
- `/agents/menu-costing`, `/agents/recipe`, `/agents/client-intake`, `/agents/menu-pricing` — task-specific RONIN-style workflows
- `/agents/ronin` — task switchboard for quick agent dispatch

## Setup

1. Clone the repository.
2. Create and activate a Python venv.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
python -m pip install -r requirements.txt
```

4. Create a `.env` file with:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
USE_MOCK_RESPONSES=false
BUILD_INDEX_ON_STARTUP=false
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_EXPIRE_MINUTES=120
CHROMA_DB_PATH=./chroma_db
SCHOOL_DIR=./chef_knowledge_data

# Option 1: single bootstrap account
AUTH_USERNAME=admin
AUTH_PASSWORD=change-me-now
AUTH_ROLES=admin

# Option 2 (recommended): multiple accounts and roles as JSON
# AUTH_USERS_JSON=[{"username":"admin","password":"change-me-now","roles":["admin"]},{"username":"chef","password":"change-me-now","roles":["chef"]},{"username":"viewer","password":"change-me-now","roles":["viewer"]}]
```

## Running Locally

> NOTE: The active source folder for this project is `C:\Users\jesse\workspace`.
> If your editor is opened on `C:\Users\jesse\47andsix-backend`, you are looking at the wrong workspace.

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Then open `index.html` or the other static pages in a browser.

## API Endpoints

### General

- `GET /` — health check
- `GET /chef/credentials` — static chef profile data
- `POST /auth/login` — returns JWT bearer token
- `GET /auth/me` — returns current authenticated user and roles

### Agent namespace

- `POST /agents/concierge`
- `POST /agents/ops`
- `POST /agents/logistics`
- `POST /agents/economics`
- `POST /agents/compliance`
- `POST /agents/memory`
- `POST /agents/menu-costing`
- `POST /agents/recipe`
- `POST /agents/client-intake`
- `POST /agents/menu-pricing`
- `POST /agents/ronin`

### AI utilities

- `POST /chat` — direct Gemini concierge conversation
- `POST /image` — generate image prompt text
- `POST /json` — request structured JSON output from Gemini
- `POST /tools` — tool-oriented operational assistance
- `POST /embed` — embed text into local ChromaDB

## Authentication and Roles

The API now uses JWT bearer tokens with role-based access control.

- `viewer` can access chef profile and chef knowledge inspection routes.
- `chef` can access operational AI routes and all `/agents/*` routes.
- `admin` has full access, including `/embed`.

Login flow:

1. `POST /auth/login` with JSON body:

```json
{
	"username": "admin",
	"password": "change-me-now"
}
```

2. Use `Authorization: Bearer <access_token>` on protected routes.

Protected routes include:

- all `/agents/*`
- `/chef-dashboard`
- `/embed`
- `/chat`, `/image`, `/json`, `/tools`, `/menu-cost`, `/event-planning`, `/inventory`
- `/chef/credentials` and `/chef/knowledge/*`

### Operations support

- `POST /menu-cost`
- `POST /event-planning`
- `POST /inventory`
- `POST /chef-dashboard`

### Chef knowledge

- `GET /chef/knowledge/files`
- `GET /chef/knowledge/portfolio`

## Chef Knowledge Data

The chef knowledge system loads training documents from `chef_knowledge/loader.py`.
Supported file formats:

- `.docx`
- `.pdf`
- `.odt`
- plain text fallback

The knowledge index is persisted in `chroma_db` and accessed through `/chef/knowledge/*` endpoints.

## Notes

- The backend is intentionally resilient if Gemini or ChromaDB are unavailable.
- `USE_MOCK_RESPONSES=true` enables a safe development fallback.
- `BUILD_INDEX_ON_STARTUP=true` triggers knowledge index refresh at startup.

## Recommended Deployment

- Use a process manager such as `uvicorn` behind a reverse proxy.
- Keep `GEMINI_API_KEY` secure.
- Store persistent ChromaDB data outside ephemeral containers.
- For production, set `USE_MOCK_RESPONSES=false` and use a stable Gemini model.

## Deploy From GitHub (Backend)

This repo is now configured for platform-backed persistent paths via:

- `CHROMA_DB_PATH` for ChromaDB persistence
- `SCHOOL_DIR` for chef knowledge source files

### Render (recommended)

1. Push this repo to GitHub.
2. In Render, create a new **Web Service** from the repo.
3. Use:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:$PORT
```

4. Add environment variables:

```env
GEMINI_API_KEY=...
JWT_SECRET_KEY=...
AUTH_USERS_JSON=[{"username":"admin","password":"change-me-now","roles":["admin"]}]
BUILD_INDEX_ON_STARTUP=true
CHROMA_DB_PATH=/var/chroma_db
SCHOOL_DIR=/var/chef_knowledge_data
USE_MOCK_RESPONSES=false
```

5. Add persistent disks:

```text
/var/chroma_db
/var/chef_knowledge_data
```

6. Deploy. Every GitHub push will auto-redeploy.

Optional: You can use the included `render.yaml` to blueprint this setup.

### Railway

1. New Project -> Deploy from GitHub.
2. Add a `Procfile` containing:

```text
web: gunicorn main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:$PORT
```

3. Set env vars:

```env
GEMINI_API_KEY=...
JWT_SECRET_KEY=...
AUTH_USERS_JSON=[{"username":"admin","password":"change-me-now","roles":["admin"]}]
BUILD_INDEX_ON_STARTUP=true
CHROMA_DB_PATH=/data/chroma_db
SCHOOL_DIR=/data/chef_knowledge_data
USE_MOCK_RESPONSES=false
```

4. Add a volume and mount it to `/data` (or directly to both folders).

5. Deploy. GitHub pushes auto-redeploy.

### Frontend Wiring (Vercel -> Backend)

After backend deploy, point frontend API base URL to your live backend domain and call with bearer token.

Frontend helper options now supported by `script.js`:

- Set `window.__API_BASE__ = "https://your-backend.onrender.com"` before loading `script.js`
- or call `setApiBase("https://your-backend.onrender.com")` at runtime (stored in localStorage)

Example:

```javascript
fetch("https://your-backend.onrender.com/agents/ronin", {
	method: "POST",
	headers: {
		"Content-Type": "application/json",
		"Authorization": `Bearer ${token}`
	},
	body: JSON.stringify({ task: "ops", message: "run schedule" })
});
```
