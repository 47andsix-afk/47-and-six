# 47-&-SIX Chef Operations Intelligence Platform

Vertical AI infrastructure for private chef and catering operations.

This repository combines:

- FastAPI backend for operational APIs
- Multi-agent orchestration for specialized workflows
- Chef knowledge indexing/search over local documents
- Willow explainability and Operating Mirror simulation
- Static task-focused frontend pages
- Role-based auth, test coverage, and deployment wiring

## Product Summary

This is not a generic chatbot project.

It is a chef operations system designed to support:

1. Menu planning and costing
2. Event planning and execution prep
3. Inventory and operational readiness
4. Decision explainability and reverse engineering
5. Long-term decision memory and scenario simulation

## Current Architecture

- `main.py`: API entrypoint, auth, route registration, lifecycle wiring
- `agents/`: specialized agent modules + orchestrator + registry
- `core/`: model config and Gemini function-calling wrapper
- `chef_knowledge/`: loader, embeddings, indexer, knowledge routes
- `willow/`: explainability + operating mirror models, engine, persistence, routes
- `tests/`: unit, integration, contract, auth, and performance guard tests
- static frontend: `index.html`, `dashboard.html`, `menu_builder.html`, `event_booking.html`, `inventory.html`, `operations_console.html`

## Key Backend Capabilities

### Core API and Auth

- JWT-style auth with roles (`viewer`, `chef`, `admin`)
- protected operational endpoints
- graceful dependency fallback behavior (503 where subsystem is unavailable)

### Agentic Operations

- orchestrator with:
  - Gemini-selected function calls
  - parallel execution
  - chained execution with dependency references
- domain agent modules for chef, ops, and menu workflows

### Chef Knowledge

- file loading and extraction
- deterministic embedding fallback
- ChromaDB persistence when available
- knowledge routes:
  - `GET /chef/knowledge/files`
  - `GET /chef/knowledge/portfolio`
  - `POST /chef/knowledge/search`

### Willow Explainability

- `POST /willow/explain`
- reversible traces
- counterfactual analysis
- uncertainty map
- branch amplitudes
- causal graph output

### Willow Operating Mirror (v0.2)

Durable, seeded, simulation-ready subsystem with SQLite persistence.

Implemented endpoints:

- `GET /willow/operating-mirror/graph`
- `POST /willow/operating-mirror/graph`
- `POST /willow/operating-mirror/graph/seed?overwrite=false|true`
- `POST /willow/operating-mirror/simulate`
- `POST /willow/operating-mirror/reverse-engineer`
- `GET /willow/operating-mirror/dashboard`
- `POST /willow/operating-mirror/decision-ledger`
- `GET /willow/operating-mirror/decision-ledger/{decision_id}`

Operating Mirror persistence tables:

- `operating_mirror_graphs`
- `operating_mirror_simulations`
- `operating_mirror_dashboard_snapshots`
- `operating_mirror_decisions`
- `operating_mirror_reverse_reviews`

## Setup

1. Create and activate virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
```

3. Create `.env`.

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
USE_MOCK_RESPONSES=false
BUILD_INDEX_ON_STARTUP=false
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_EXPIRE_MINUTES=120
CHROMA_DB_PATH=./chroma_db
SCHOOL_DIR=./chef_knowledge_data
OPERATING_MIRROR_DB_PATH=./chroma_db/operating_mirror.db

# Option A: bootstrap single account
AUTH_USERNAME=admin
AUTH_PASSWORD=change-me-now
AUTH_ROLES=admin

# Option B: multiple role accounts
# AUTH_USERS_JSON=[{"username":"admin","password":"change-me-now","roles":["admin"]},{"username":"chef","password":"change-me-now","roles":["chef"]},{"username":"viewer","password":"change-me-now","roles":["viewer"]}]
```

## Run Locally

```powershell
uvicorn main:app --app-dir D:\workspace\repos\workspace --host 127.0.0.1 --port 8000 --reload
```

Run tests:

```powershell
python -m pytest -q
```

Optional marker runs:

```powershell
python -m pytest -q -m "not perf"
python -m pytest -q -m perf
```

## Frontend Usage

Pages are static and call the API at `http://127.0.0.1:8000` by default.

Shared API helper is in `script.js` and supports:

- runtime base URL override with `window.__API_BASE__`
- stored base URL via `setApiBase(...)`
- bearer token management for protected routes

## Quality Baseline

Current suite includes:

- app smoke
- orchestrator behavior
- chef knowledge behavior
- willow logic and API integration
- auth negative paths and schema contracts
- openapi contract checks
- operating mirror flow tests

## Deployment

- Render config: `render.yaml`
- Cloud Build config: `cloudbuild.yaml`
- Process start profile: `Procfile`

Recommended production settings:

1. Keep `USE_MOCK_RESPONSES=false`
2. Set strong `JWT_SECRET_KEY`
3. Persist `CHROMA_DB_PATH` and Operating Mirror DB path
4. Secure API keys via provider secret manager

## Product Direction

The current milestone is **Operating Mirror v0.2**:

- durable causal graph state
- seedable default graph
- deterministic simulation with causal path tracing
- richer dashboard schema (`top_causal_paths`, `risk_panel`, `recommended_actions`)
- reverse-engineering root-cause ranking with recommended fixes

Next planned direction:

1. simulation/review retrieval endpoints by ID and query filters
2. longitudinal dashboard reporting
3. tighter causal-path assertions and calibration tooling

## License / Ownership

Internal project for 47-&-SIX operations platform development.
