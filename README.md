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
# 47-&-SIX

Private chef systems, class portfolio, and operational tooling built around real cooking work, disciplined training, and a high-performance private service model.

## What This Is

47-&-SIX is both a public-facing chef brand and a private operations portal. The public site presents the concept, class work, and service story. The private portal supports planning, costing, inventory, event prep, and internal decision-making.

This project is intentionally practical. It is meant to support a real culinary business, not just demonstrate code.

## Concept

**The Daily Stack: Private Culinary Systems** is a mobile private chef and catering concept serving El Paso, TX, especially the Upper Valley and West Side Estates. The service is built around:

- on-site private dining
- breakfast-to-dinner support
- cooler-based meal and hydration prep
- family lifestyle integration
- clean, safe, high-discipline kitchen execution

The concept is designed for households and professionals who want more than a meal. They want a system that saves time, reduces stress, and keeps people fueled.

## Chef Background

Cooking started young, standing on a chair to reach the counter and learn from family. The kitchen ethic was simple:

- clean cook
- safe cook
- stay organized
- respect the food

That foundation shaped the way this business operates now. The goal is still the same: make food that matters, keep the process clean, and serve people with care.

## Education and Training

Current culinary training includes:

- CU101 Culinary Foundations
- CU122 Culinary Arts and Patisserie
- CU132 World Cuisines
- CU222 The Farm to Table Kitchen
- CE160 Culinary Entrepreneurship
- CE167 Purchasing and Cost Control
- CE187 Menu Design and Management
- OR120-O Culinary Student Orientation

Current status:

- finished walking July 28
- in externship phase
- completing hours through private chef work
- balancing school, business, and portfolio building

## Class Portfolio

The class menu and plate portfolio live in [class_menu.html](class_menu.html). It includes CU222 dishes such as:

- Honey Granola
- Pan Toasted Nuts
- Dukkah
- Black Bean Burger
- Arroz con Pollo
- Fish en Papillote
- Cauliflower Steak
- Chicken Confit
- Gravlax
- Farmer’s Cheese

The page also includes photo slots for plated work so real images can be added as the portfolio grows.

## Public Site and Private Portal

The site is split into two clear experiences:

- **Public homepage**: brand, concept, services, story, and contact path
- **Private portal**: login-protected tools for dashboard, menu costing, inventory, event planning, and operations console

This split keeps the client-facing site polished while protecting the internal workflow.

## Business Model

The business is built as a premium private chef and catering operation with a structured weekly rhythm:

- Friday through Monday: primary service, high-margin dinners, private events, and catering
- Tuesday through Thursday: planning, sourcing, cooler prep, and meal drops

The model focuses on long-term household relationships, trust, and repeatable service rather than one-time plates.

## Target Market

The ideal client is a high-net-worth household, founder, or professional who values:

- time
- health
- privacy
- consistency
- manual mastery

Typical clients may include busy families, tech founders, surgeons, executives, and other high-demand households.

## Website Features

The frontend includes:

- public marketing and concept pages
- private portal login flow
- class menu portfolio page
- plate photo gallery scaffolding
- dashboard, menu, inventory, event, and operations pages

## Backend Features

The FastAPI backend supports:

- role-based authentication
- private operational endpoints
- chef knowledge retrieval
- Willow explainability
- Operating Mirror v0.2 simulation and persistence
- fallback/mock mode for safe development

## Tech Stack

- FastAPI backend
- static HTML/CSS/JS frontend
- agent orchestration
- knowledge indexing/search
- SQLite persistence for operational mirror state
- Google OAuth and Gemini configuration support

## Local Run

```powershell
uvicorn main:app --app-dir D:\workspace\repos\workspace --host 127.0.0.1 --port 8000 --reload
```

## Environment Variables

Create a local `.env` file with the following values:

```env
GEMINI_API_KEY=your_api_key_here
ENABLE_PAID_AI=true
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback
USE_MOCK_RESPONSES=false
BUILD_INDEX_ON_STARTUP=false
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_EXPIRE_MINUTES=120
CHROMA_DB_PATH=./chroma_db
SCHOOL_DIR=./chef_knowledge_data
OPERATING_MIRROR_DB_PATH=./chroma_db/operating_mirror.db

AUTH_USERNAME=admin
AUTH_PASSWORD=change-me-now
AUTH_ROLES=admin
```

## Deployment Notes

- GitHub Pages can host the public site
- Render or another host can run the FastAPI backend
- OAuth redirect URIs must match the deployed backend exactly
- Keep live API keys out of the frontend and out of version control

## Final Note

This project is the bridge between culinary training and a real private chef business. It is meant to show the system behind the food: discipline, logistics, hospitality, and the ability to build something dependable from real experience.
