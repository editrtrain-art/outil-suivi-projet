# NEXUS — Digital Project Tracking & Control

> Enterprise-grade web application for **Project Control**, **Earned Value Management (EVM)**, **Resource Leveling**, and **Critical Path Method (CPM)** scheduling.

## Overview

NEXUS replaces fragmented project tracking tooling (Excel, MS Project, Jira, Trello) with a unified, real-time platform covering resource planning, physical progress tracking, schedule management, and deliverable validation.

**Version:** 3.0 — Multi-Baselines, Resource Leveling & AI Predictive Engine

## Tech Stack

| Layer | Technology | Version |
|:------|:-----------|:--------|
| **Frontend** | Next.js (App Router) | 15.x |
| **Frontend Language** | TypeScript | 5.7 |
| **UI Components** | shadcn/ui + Tailwind CSS | 3.x |
| **Client State** | TanStack Query + Zustand | 5.x |
| **Visualization** | Recharts + D3.js | 2.x |
| **Backend API** | FastAPI | 0.115 |
| **Backend Language** | Python | 3.12 |
| **ORM** | SQLAlchemy | 2.0 |
| **Database** | PostgreSQL | 16 |
| **Authentication** | Clerk | — |
| **Hosting** | Vercel (Serverless) | — |

## Project Structure

```
nexus/
├── apps/
│   ├── backend/                # FastAPI Python API
│   │   ├── app/
│   │   │   ├── core/           # Config, DB, auth, middleware
│   │   │   ├── domain/
│   │   │   │   ├── models/     # SQLAlchemy ORM models
│   │   │   │   ├── schemas/    # Pydantic v2 DTOs
│   │   │   │   └── services/   # Business logic (CPM, EVM, Leveling)
│   │   │   ├── routers/        # API endpoints
│   │   │   └── utils/          # Helpers (dates, export, import)
│   │   ├── alembic/            # DB migrations
│   │   └── tests/              # Unit, integration, performance
│   └── frontend/               # Next.js 15 App Router
│       ├── app/                # Pages and layouts
│       ├── components/         # Reusable UI components
│       ├── hooks/              # TanStack Query hooks
│       ├── lib/                # API client, utilities
│       └── types/              # TypeScript interfaces
└── packages/
    └── shared/                 # Shared types and constants
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (Supabase or Neon)

### Backend

```bash
cd apps/backend
python -m venv .venv
.venv/Scripts/activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

## License

Proprietary — JESA S.A. All rights reserved.
