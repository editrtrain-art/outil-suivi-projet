# MASTER GUIDELINES V3 — NEXUS
## Digital Project Tracking & Control Web Application
### Version 3.0 — Multi-Baselines, Resource Leveling & AI Predictive Engine

**Date:** May 24, 2026
**Project Code:** NEXUS *(formerly Antigravity)*
**Classification:** Technical Specifications & Execution Framework
**Language:** English (EN) throughout
**Status:** Approved for Execution

---

## TABLE OF CONTENTS

1. [Executive Summary & Version Changelog](#section-1)
2. [Feasibility & Adoption Strategy](#section-2)
3. [Conceptual Design — Functional Architecture](#section-3)
4. [Basic Design — Technical Architecture](#section-4)
5. [Detailed Design — Data Model](#section-5)
6. [Detailed Design — Business Algorithms](#section-6)
7. [Implementation Planning — 20 Phases / 8 Sprints](#section-7)
8. [Governance & Deliverables Matrix](#section-8)
9. [Annexes](#section-9)

---

## SECTION 1 — EXECUTIVE SUMMARY & VERSION CHANGELOG {#section-1}

### 1.1 What is NEXUS?

NEXUS is an enterprise-grade web application dedicated to **Project Control**, **Resource Leveling**, and **Earned Value Management (EVM)** for digital and IT projects. It provides teams with a unified, real-time platform that replaces fragmented tooling (Excel, MS Project, Jira, Trello) with a single source of truth covering resource planning, physical progress tracking, schedule management, and deliverable validation.

NEXUS is built on a **serverless architecture** deployed on Vercel, with a FastAPI Python backend and a Next.js 15 frontend, targeting automatic scalability, zero infrastructure management, and rapid time-to-market.

### 1.2 Strategic Objectives

| Objective | Target |
|:---|:---|
| Reduce monthly progress consolidation effort | −40% vs manual process |
| Proactive alert on schedule or cost drift | SPI < 0.95 or CPI < 0.90 flagged within 24h |
| New project onboarding time | Under 15 minutes (with import) |
| Concurrent project capacity | 50 projects, 200 users, no infra change |
| API response time (p95) | < 800 ms |
| CPM recalculation after dependency change | < 2 seconds |

### 1.3 Version Changelog

| Version | Key Additions | Status |
|:---|:---|:---|
| **V1** | FastAPI + React/Vue concept, basic EVM (SPI/CPI), EVM formulas, WBS, S-curves, Gantt | Archived |
| **V2** | Vercel serverless architecture, Next.js 15, complete DDL schema with UUID/indexes, full CPM engine (forward/backward pass), complete EVM suite (SPI/CPI/EAC/VAC/TCPI), 4-role RBAC via Clerk, deliverable workflow state machine, multi-workspace isolation with RLS | Reference baseline |
| **V3 (current)** | **MUST:** Native Excel/MS Project import, Resource Leveling algorithm, Multi-Baselines management, Risk Register with contingency linkage. **SHOULD:** In-app notifications, Global audit trail, Calendar view, AI Predictive Engine (M7) | **Active** |

### 1.4 What is Out of Scope for V3 (Backlog V4+)

The following capabilities have been explicitly deferred to V4 or beyond:

- Real-time WebSocket collaboration (requires stateful infrastructure)
- Native dark mode (shadcn/ui supports it; low implementation effort, deferred for UX consistency)
- Multi-currency support (DH remains the default unit; internationalization deferred)
- Native webhooks integrations (Jira, GitHub, Azure DevOps)
- Project template library
- Custom report builder with drag-and-drop layout
- Native mobile application (PWA responsive is V3 target)

---

## SECTION 2 — FEASIBILITY & ADOPTION STRATEGY {#section-2}

### 2.1 Problem Statement

The core adoption friction in existing project control tools is **onboarding latency**: teams already have projects structured in Excel or MS Project and refuse to re-enter data manually. NEXUS V3 directly addresses this by introducing native import parsers as a first-class feature, not an afterthought.

Secondary friction points addressed in V3:
- Resource managers need to see overloads resolved automatically, not just highlighted.
- Project managers need to compare re-baselined schedules against original commitments.
- Stakeholders need risk visibility connected directly to schedule impact.

### 2.2 Technology Stack — Validated

| Layer | Technology | Version | Rationale |
|:---|:---|:---|:---|
| **Frontend** | Next.js (App Router) | 15.x | Native Vercel deployment, SSR/ISR, React Server Components |
| **Frontend Language** | TypeScript | 5.7 | Strong typing, maintainability |
| **UI Components** | shadcn/ui + Tailwind CSS | 3.x | Accessible, customizable design system |
| **Client State & Data** | TanStack Query (React Query) | 5.x | Server cache, optimistic sync, stale-while-revalidate |
| **Local State** | Zustand | 5.x | Lightweight, persistence middleware |
| **Visualization** | Recharts + D3.js | 2.x | S-curves, histograms, Gantt SVG |
| **Backend API** | FastAPI | 0.115 | ASGI async, OpenAPI auto-doc, dependency injection |
| **Backend Language** | Python | 3.12 | Data ecosystem (Pandas/NumPy for EVM vectorization), CPM recursion |
| **ORM** | SQLAlchemy | 2.0 | Native async, complex relational modeling |
| **DB Migrations** | Alembic | 1.13 | Versioned schema management |
| **DB Driver** | asyncpg | 0.30 | High-performance async PostgreSQL driver |
| **Database** | PostgreSQL | 16 | Relational integrity, JSONB, RLS, analytical windows |
| **DB Hosting** | Supabase / Neon | — | PgBouncer pooling, backups, branching |
| **Cache / Session** | Vercel KV (Redis) | 7.x | Stateless serverless state, JWT cache, rate limiting |
| **Authentication** | Clerk | — | JWT, 4-role RBAC, SSO, user webhooks |
| **File Storage** | Vercel Blob / AWS S3 | — | Deliverable attachments, import files |
| **Async Jobs (optional)** | Upstash QStash | — | Heavy report generation, scheduled alerts |
| **Backend Tests** | pytest + pytest-asyncio | 8.x | Async fixtures, unit and integration tests |
| **E2E Tests** | Playwright | 1.49 | Browser-automated critical path tests |
| **CI/CD** | GitHub Actions | — | Lint, test, build, deploy to Vercel |
| **Monitoring** | Sentry + Vercel Analytics | — | Error tracking, Web Vitals |

### 2.3 Vercel Serverless — Constraints & Mitigations

| Constraint | Impact | Mitigation Strategy |
|:---|:---|:---|
| Timeout 10s (Hobby) / 60s (Pro) | Heavy CPM computations | Async jobs via QStash for large graphs; Pro plan for production |
| Python cold start ~200–500ms | First request latency | Keep-alive cron ping, minimal package footprint, lazy loading |
| Bundle size ≤ 50 MB | Pandas/NumPy weight | External computation layer or vectorized logic only on server |
| Stateless mandatory | No in-memory session | JWT stateless + Redis KV for cache and session storage |
| No persistent filesystem | File upload handling | Vercel Blob / S3 for all deliverable and import file storage |

### 2.4 Scalability Model

- **Frontend:** CDN Edge (Vercel Edge Network) — unlimited scaling.
- **Python API:** Per-request scaling (1 instance per invocation). DB connection is the limiting factor.
- **Database:** Vertical scaling (Supabase/Neon) + read replicas if > 1,000 connections/s.
- **Connection pooling:** PgBouncer (transaction mode) on provider side + `asyncpg` pool (min 2, max 10) on application side.
- **Capacity target:** 50 active projects, 200 users, 5,000 tasks, 10,000 progress entries/month, 99.9% uptime.

### 2.5 Risk Register — Project Risks

| ID | Risk | Probability | Impact | Mitigation |
|:---|:---|:---|:---|:---|
| R01 | CPM engine complexity at scale | Medium | High | Unit-tested and benchmarked on 1,000-task graphs |
| R02 | Python cold starts on Vercel | High | Medium | Warm-up cron, Pro plan, lightweight packages |
| R03 | DB connection leaks | Medium | High | Strict pooling, connection timeout, health checks |
| R04 | Import parser edge cases (Excel/MPP) | High | Medium | Validation layer with per-row error reporting |
| R05 | Resource leveling non-convergence | Medium | Medium | Max-iteration cap, fallback to manual suggestion mode |
| R06 | LLM latency in AI module | Medium | Low | Async background job, results cached, not blocking UI |
| R07 | Unexpected Vercel cost overrun | Low | Medium | Budget alerts, usage monitoring, query optimization |
| R08 | Data isolation failure (multi-tenant) | Low | High | RLS on all tenant-sensitive tables, integration tests |

---

## SECTION 3 — CONCEPTUAL DESIGN — FUNCTIONAL ARCHITECTURE {#section-3}

### 3.1 Vision & User Personas

**Persona 1 — Digital Project Manager (Karim)**
- Need: Consolidated portfolio view, delay alerts, overloaded resources, baseline comparison.
- Frequency: Daily (morning dashboard review).

**Persona 2 — Resource Manager (Samira)**
- Need: Workload histogram, capacity vs. allocation, automatic leveling suggestions.
- Frequency: Weekly (resource smoothing session).

**Persona 3 — Developer / Contributor (Youssef)**
- Need: My tasks today, progress entry, deliverable submission.
- Frequency: Daily (time and progress logging).

**Persona 4 — Director / Sponsor**
- Need: Monthly PDF report, S-curves, synthetic EVM indicators, risk heat map.
- Frequency: Monthly (steering committee).

### 3.2 Functional Scope — V3

**In Scope (V3 Perimeter):**
- Multi-workspace management with full data isolation.
- Full CRUD: projects, phases, tasks, sub-tasks (WBS up to 5 levels).
- Inter-task dependencies (FS, SS, FF, SF) with lag/lead values.
- CPM engine with automatic Early/Late date recalculation.
- Nominative and generic (role-based) resource assignment.
- Physical progress entry (%) and actual hours consumed.
- Full EVM suite: PV, EV, AC, SPI, CPI, EAC (enhanced), VAC, TCPI.
- **[V3-MUST]** Native Excel and MS Project file import with validation report.
- **[V3-MUST]** Automatic resource leveling using free float consumption.
- **[V3-MUST]** Multi-baseline management with graphical comparison.
- **[V3-MUST]** Risk Register connected to tasks with contingency coefficients.
- Deliverable register with 4-state workflow: Draft → Submitted → In Review → Approved/Rejected.
- Interactive dashboards: Gantt, EVM S-curves, resource histograms.
- Data exports: CSV, Excel (formatted), PDF report.
- JWT authentication, 4-role RBAC (Admin, PM, Contributor, Viewer).
- **[V3-SHOULD]** In-app notification center.
- **[V3-SHOULD]** Global audit trail across all entities.
- **[V3-SHOULD]** Calendar view of tasks, milestones, and deliverables.
- **[V3-SHOULD]** AI Predictive Engine: LLM-based drift alerts from progress logs.

**Out of Scope (V4+):**
- Real-time WebSocket collaboration.
- Native dark mode.
- Multi-currency support.
- Native Jira/GitHub/Azure DevOps webhook integrations.
- Project template library.
- Custom report builder.

### 3.3 Functional Modules

#### M0 — Authentication & Multi-Workspace Management
- User registration and login via Clerk (email/password, Google OAuth, enterprise SSO).
- Workspace creation with tenant isolation (slug, plan type, settings).
- Member invitation by role (Admin, PM, Contributor, Viewer).
- User profile, preferences, notification settings.
- Row-Level Security enforcement at the database level per workspace.

#### M1 — Resources & Capacity
- **Resource profiles:** Name, role (Senior Developer, Junior Developer, Architect, QA, etc.), skill tags, hourly rate (DH/h), active status, entry and exit dates.
- **Resource calendars:** Definition of working days, public holidays (Moroccan calendar by default, configurable), personal leave per resource.
- **Capacity computation:** Available hours per month = working days × 8h, minus leave days. Adjustable.
- **Cost modeling:** Hourly rate × planned hours = forecasted cost per task and per project. Supports nominative rates (e.g., Abd el Malek El Mallouki at 800 DH/h, Bahae Eddine Moutaoukil at 400 DH/h).
- **[V3-MUST] Resource Leveling:** Automatic detection of over-allocated resources; non-critical tasks shifted forward within their available free float to eliminate overloads without extending the project end date. Full leveling report produced (tasks shifted, new dates, unresolvable overloads flagged).

#### M2 — Planning, WBS & CPM Engine
- **WBS structure:** Project → Phase → Work Package → Task → Sub-task (5 levels). Auto-generated WBS codes (1.0, 1.1, 1.1.1, etc.).
- **Task attributes:** Name, description, assigned resource(s), planned start/finish dates, duration (days), relative weight (%), milestone flag, priority (1–5), status.
- **Multi-resource assignment:** 1..N resources per task, each with an allocation percentage.
- **Dependencies:** Finish-to-Start (FS), Start-to-Start (SS), Finish-to-Finish (FF), Start-to-Finish (SF), with positive lag and negative lead values in days.
- **CPM Engine:** Forward pass (Early Start / Early Finish), Backward pass (Late Start / Late Finish), Total Float and Free Float computation, Critical Path identification (Total Float = 0). Automatic recalculation triggered on every dependency, duration, or constraint change. Recalculation target: < 2 seconds for up to 1,000 tasks.
- **Gantt visualization:** Timeline with task bars colored by status, critical path bars highlighted, milestones as diamonds, dependency arrows, today line, progress overlay showing EV vs. PV.
- **[V3-MUST] Multi-Baselines:** Store and name multiple planning snapshots (e.g., Baseline B0 Initial, B1 Amendment 1, B2 Amendment 2). Graphically compare timelines across baselines. EVM calculations always reference the user-selected active baseline. Baseline locking is irreversible per snapshot (append-only).

#### M3 — Project Controls & EVM
- **Baseline lock:** Once a baseline is activated, the reference schedule and budget are frozen for that snapshot. Progress is always measured against the active baseline.
- **Progress entry:** Weekly or monthly. Physical completion (%), actual hours consumed (AC), entry date, notes. One entry per (task, date) pair enforced.
- **WBS roll-up:** Physical percent and EVM metrics aggregate upward from task → phase → project, weighted by relative weight percentages.
- **EVM indicators:** PV, EV, AC, SPI, CPI, EAC (enhanced formula), VAC, TCPI (see Section 6).
- **S-curve data:** Cumulative PV (planned), EV, and AC over the project timeline, generated weekly from baseline and progress logs.
- **Alerting:** Configurable thresholds — SPI < 0.95 (schedule slip), CPI < 0.90 (cost overrun), resource overload > 110%, deliverable past due date. Alerts trigger in-app notifications and are visible on all dashboards.

#### M4 — Deliverables & Validation Workflow
- **Deliverable register:** Name, description, parent task, responsible submitter, target date, file attachment (Blob/S3), status.
- **4-state workflow:** Draft → Submitted (by Contributor) → In Review (by PM) → Approved or Rejected (with mandatory comment if rejected). Rejected deliverables return to Draft for revision.
- **Access control:** Only assigned contributors may submit; only PM or Admin may approve or reject.
- **File upload:** Accepted formats — PDF, Word, Excel, PNG, ZIP. Maximum file size: 20 MB.
- **Audit trail:** Every state transition is recorded with actor identity, timestamp, and comment.
- **Notifications:** PM is notified on submission; contributor is notified on rejection or approval.

#### M5 — Reporting & Export
- **Project dashboard:** Gantt view, EVM summary cards (SPI, CPI, EAC, VAC, TCPI), S-curves, active alerts, upcoming milestones, top delayed tasks.
- **Portfolio dashboard:** Multi-project SPI/CPI health matrix, consolidated budget overview.
- **Resource histogram:** Monthly allocated hours vs. capacity per resource, colored by utilization band (green < 80%, orange 80–100%, red > 100%).
- **Calendar view [V3-SHOULD]:** Monthly calendar showing tasks, milestones, and deliverables with color coding by type.
- **Excel export:** Multi-tab workbook (simplified Gantt, EVM data, resource workload, deliverables list). Conditional formatting applied for SPI/CPI status.
- **PDF report:** Monthly synthesis report with cover page, executive summary, KPI cards, S-curve chart, alerts list, deliverable status summary.

#### M6 — Risk Register [V3-MUST]
- **Risk catalog:** Each risk has a title, category (Technical, Schedule, Budget, Resource, External, Quality), description, probability score (1–5), impact score (1–5), computed risk score (Probability × Impact), mitigation plan, owner, and status (Active / Mitigated / Closed).
- **Risk-task linkage:** A risk can be linked to one or more tasks. When a linked risk's score exceeds a configurable criticality threshold (default: score ≥ 15), the system automatically applies a **contingency coefficient** to that task's duration (e.g., +15%), extending its end date and triggering a CPM recalculation.
- **Risk matrix visualization:** Interactive 5×5 heatmap displaying all active risks positioned by probability and impact quadrant.
- **Risk tracking:** Progress notes with timestamps can be added to each risk entry. An aggregate project risk score is computed as the weighted average of all active risk scores.

#### M7 — AI Predictive Engine [V3-SHOULD]
- **Data source:** All `progress_logs` entries for the project, aggregated weekly — physical percent completed, actual hours consumed, planned hours, resource assignment.
- **Analysis approach:** A background LLM agent (Claude Sonnet via Anthropic API, invoked asynchronously) analyzes the productivity trend pattern: rate of budget consumption vs. physical progress, consistency of weekly reporting cadence, correlation between SPI decline and specific work packages.
- **Output:** Contextualized textual alerts surfaced on the project dashboard, distinct from threshold-based EVM alerts. Examples: *"At current EV growth rate, the project will reach 80% completion by Week 32 instead of Week 28. Slippage concentrated in Phase 2 tasks assigned to Youssef (3 consecutive weeks below planned velocity)."*
- **Invocation model:** Triggered manually by the PM (on-demand analysis button) or automatically at each monthly period close. Results are cached and displayed as an "AI Insights" panel on the dashboard. Never blocks the UI.
- **Scope boundary:** The AI module reads data, never writes or modifies planning data. It is strictly advisory.

#### M8 — Notifications & Audit Trail [V3-SHOULD]
- **In-app notifications:** Bell icon in header showing unread count badge. Notification center listing all events sorted by recency. Notifications are generated by: EVM threshold alerts, deliverable state transitions, workspace member invitations, risk criticality threshold breach, AI insight availability.
- **Notification management:** Mark as read (individual or all). Notifications are persisted in the database and visible across sessions.
- **Global audit trail:** Every create, update, and delete operation on core entities (projects, tasks, dependencies, resources, baselines, deliverables, risks) is recorded with the entity type, entity ID, action performed, previous value (JSONB), new value (JSONB), user identity, timestamp, and IP address. Audit log is append-only, paginated, filterable by entity type, user, and date range.

---

## SECTION 4 — BASIC DESIGN — TECHNICAL ARCHITECTURE {#section-4}

### 4.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│           Browser (Next.js 15)   /   Mobile Web (PWA)       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS / JSON
┌─────────────────────────────────────────────────────────────┐
│                  VERCEL EDGE NETWORK                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       FRONTEND — Next.js 15 App Router               │  │
│  │  React Server Components · ISR · Edge Middleware     │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │ API Routes / Server Actions         │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │       BACKEND API — FastAPI (Python Serverless)      │  │
│  │  /api/v1/auth      → Clerk JWT validation            │  │
│  │  /api/v1/projects  → CRUD, WBS, baselines            │  │
│  │  /api/v1/planning  → CPM, dependencies, leveling     │  │
│  │  /api/v1/evm       → Progress logs, indicators       │  │
│  │  /api/v1/resources → Resource profiles, workload     │  │
│  │  /api/v1/deliverables → Workflow, file upload        │  │
│  │  /api/v1/risks     → Risk register, matrix           │  │
│  │  /api/v1/reports   → Excel/PDF export                │  │
│  │  /api/v1/ai        → Predictive engine (async)       │  │
│  │  /webhooks/clerk   → User sync                       │  │
│  └────────────────────┬─────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  PostgreSQL 16   Vercel KV       Vercel Blob
  (Supabase)      (Redis)         (S3-compatible)
  Primary DB      Cache/Session   File Storage
```

### 4.2 Backend Project Structure

```
apps/backend/
├── app/
│   ├── main.py                  # FastAPI app instantiation, CORS, middleware
│   ├── core/
│   │   ├── config.py            # Settings (Pydantic BaseSettings, env vars)
│   │   ├── database.py          # SQLAlchemy async engine and session factory
│   │   ├── dependencies.py      # get_db(), get_current_user() from Clerk JWT
│   │   ├── permissions.py       # require_role(), require_workspace_member()
│   │   ├── exceptions.py        # NotFoundError, ForbiddenError, ConflictError
│   │   ├── middleware.py        # Request logging with timing
│   │   └── audit.py             # @audit_log decorator
│   ├── domain/
│   │   ├── models/              # SQLAlchemy ORM models (one file per entity)
│   │   ├── schemas/             # Pydantic v2 DTOs (request / response)
│   │   └── services/            # Business logic (pure, stateless)
│   │       ├── cpm_engine.py    # CPM forward/backward pass algorithm
│   │       ├── evm_calculator.py
│   │       ├── resource_leveler.py   # [V3] Leveling algorithm
│   │       ├── baseline_service.py   # [V3] Multi-baseline management
│   │       ├── risk_service.py       # [V3] Risk register + contingency
│   │       ├── ai_engine.py          # [V3] LLM predictive analysis
│   │       └── import_parser.py      # [V3] Excel / MS Project parser
│   ├── routers/
│   │   ├── auth.py
│   │   ├── workspaces.py
│   │   ├── projects.py
│   │   ├── planning.py
│   │   ├── evm.py
│   │   ├── resources.py
│   │   ├── deliverables.py
│   │   ├── risks.py             # [V3]
│   │   ├── notifications.py     # [V3]
│   │   ├── reports.py
│   │   ├── ai.py                # [V3]
│   │   └── webhooks.py
│   └── utils/
│       ├── date_utils.py        # Working days computation
│       ├── excel_importer.py    # [V3] Import parser utility
│       ├── excel_exporter.py    # Export formatter
│       └── pdf_generator.py
├── alembic/                     # DB migrations
├── tests/
│   ├── unit/                    # CPM, EVM, leveling, risk algorithms
│   ├── integration/             # API endpoints, RBAC, workflow
│   └── performance/             # CPM and EVM load benchmarks
├── requirements.txt
├── requirements-dev.txt
└── vercel.json
```

### 4.3 Frontend Project Structure

```
apps/frontend/
├── app/
│   ├── layout.tsx               # Root layout (ClerkProvider, QueryClientProvider)
│   ├── (auth)/                  # Unauthenticated routes (login, register)
│   └── (app)/                   # Protected routes
│       ├── layout.tsx           # Sidebar + Header
│       ├── workspaces/
│       ├── [workspaceId]/
│       │   ├── projects/
│       │   │   └── [id]/
│       │   │       ├── dashboard/
│       │   │       ├── planning/   # WBS + Gantt + Resource views
│       │   │       ├── evm/
│       │   │       ├── deliverables/
│       │   │       ├── risks/      # [V3]
│       │   │       ├── calendar/   # [V3]
│       │   │       └── baselines/  # [V3]
│       │   ├── portfolio/
│       │   ├── resources/
│       │   └── my-tasks/
├── components/
│   ├── layout/
│   ├── ui/                      # Design system tokens and base components
│   ├── dashboard/
│   ├── planning/                # WBSTree, GanttChart, DependencyManager
│   ├── evm/                     # SCurveChart, EVMCards, ProgressLogForm
│   ├── resources/               # WorkloadHistogram, ResourceCalendar
│   ├── deliverables/
│   ├── risks/                   # [V3] RiskMatrix, RiskTable
│   ├── baselines/               # [V3] BaselineComparator
│   └── ai/                      # [V3] AIInsightsPanel
├── hooks/                       # TanStack Query hooks per domain
├── lib/
│   └── api/                     # Axios client with Clerk token interceptor
├── types/                       # TypeScript interfaces
└── middleware.ts                # Auth route protection
```

### 4.4 Performance & Caching Strategy

| Layer | Strategy | TTL |
|:---|:---|:---|
| CPM results per project | Vercel KV cache — invalidated on any planning change | 1h |
| EVM indicators per project | Vercel KV cache — invalidated on new progress log | 24h |
| Clerk JWKS keys | Vercel KV cache | 1h |
| React Query (client) | Stale-while-revalidate | 30s stale / 5min cache |
| Next.js ISR pages | Static regeneration for public-facing pages | 60s |
| Gantt with 1,000+ tasks | `react-window` virtualization | — |

### 4.5 Security Model

- **Authentication:** Clerk JWT — all API endpoints validate the Bearer token on every request via `get_current_user()` dependency.
- **Authorization:** RBAC enforced at the API layer. Viewer cannot mutate. Contributor cannot approve deliverables. PM cannot manage workspace billing. Admin has full access.
- **Data isolation:** PostgreSQL Row-Level Security (RLS) policies on all workspace-scoped tables. Cross-workspace data leakage is structurally impossible at the DB level.
- **File uploads:** Type and size validated before storage. Files stored in Vercel Blob / S3 with signed URLs. No direct user access to raw storage paths.
- **Audit trail:** All mutations produce an audit log entry. Log is append-only. No delete endpoint exposed.
- **Webhook verification:** Clerk webhook events verified via `svix-signature` header before processing.

---

## SECTION 5 — DETAILED DESIGN — DATA MODEL {#section-5}

### 5.1 Entity-Relationship Overview

Core entities and their relationships:

```
Workspace ──< WorkspaceMember >── User
Workspace ──< Project ──< Phase ──< Task
                                     Task ──< Task (self-referential sub-tasks)
                                     Task ──< TaskDependency
                                     Task ──< TaskAssignment >── Resource
                                     Task ──< ProgressLog
                                     Task ──< Deliverable ──< DeliverableEvent
                                     Task ──< RiskTaskLink >── Risk [V3]
Project ──< ProjectBaseline [V3]
Project ──< Risk [V3]
Workspace ──< Resource ──< ResourceCalendar
User ──< Notification [V3]
Workspace ──< AuditLog [V3]
```

### 5.2 Core Table Definitions (DDL — PostgreSQL 16)

#### Workspaces

```sql
CREATE TABLE workspaces (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(120) NOT NULL,
    slug          VARCHAR(120) UNIQUE NOT NULL,
    created_by    UUID NOT NULL,
    plan_type     VARCHAR(20) DEFAULT 'free'
                  CHECK (plan_type IN ('free','pro','enterprise')),
    settings      JSONB DEFAULT '{}',
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

#### Users

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY,          -- Clerk user_id
    email         VARCHAR(255) UNIQUE NOT NULL,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    avatar_url    TEXT,
    role_global   VARCHAR(20) DEFAULT 'user'
                  CHECK (role_global IN ('user','admin')),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

#### Workspace Members

```sql
CREATE TABLE workspace_members (
    workspace_id  UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
    role          VARCHAR(20) NOT NULL
                  CHECK (role IN ('admin','pm','contributor','viewer')),
    joined_at     TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (workspace_id, user_id)
);
```

#### Projects

```sql
CREATE TABLE projects (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id         UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name                 VARCHAR(200) NOT NULL,
    description          TEXT,
    start_date           DATE NOT NULL,
    end_date             DATE NOT NULL,
    budget_total         DECIMAL(15,2) DEFAULT 0,
    status               VARCHAR(30) DEFAULT 'draft'
                         CHECK (status IN ('draft','active','on_hold','completed','cancelled')),
    active_baseline_id   UUID,               -- FK set after baseline creation [V3]
    pm_user_id           UUID REFERENCES users(id),
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_projects_workspace ON projects(workspace_id, status);
```

#### Project Baselines [V3-MUST]

```sql
CREATE TABLE project_baselines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_code    VARCHAR(20) NOT NULL,    -- e.g. 'B0', 'B1', 'B2'
    description     TEXT,
    snapshot        JSONB NOT NULL,          -- Full planning snapshot at lock time
    locked_by       UUID REFERENCES users(id),
    locked_at       TIMESTAMPTZ DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT false,
    UNIQUE (project_id, version_code)
);
CREATE INDEX idx_baselines_project ON project_baselines(project_id, is_active);
```

*Rule: Only one baseline per project may have `is_active = true` at any time (enforced at service layer). Baselines are immutable once created.*

#### Phases

```sql
CREATE TABLE phases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    wbs_code        VARCHAR(50) NOT NULL,
    order_index     INT DEFAULT 0,
    weight_percent  DECIMAL(5,2) DEFAULT 0
                    CHECK (weight_percent BETWEEN 0 AND 100),
    planned_start   DATE,
    planned_finish  DATE,
    UNIQUE (project_id, wbs_code)
);
```

#### Tasks

```sql
CREATE TABLE tasks (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phase_id              UUID NOT NULL REFERENCES phases(id) ON DELETE CASCADE,
    parent_task_id        UUID REFERENCES tasks(id) ON DELETE CASCADE,
    baseline_id           UUID REFERENCES project_baselines(id),    -- [V3]
    name                  VARCHAR(255) NOT NULL,
    wbs_code              VARCHAR(50) NOT NULL,
    description           TEXT,
    duration_days         INT DEFAULT 1 CHECK (duration_days >= 0),
    start_date_scheduled  DATE,
    end_date_scheduled    DATE,
    start_date_actual     DATE,
    end_date_actual       DATE,
    early_start           DATE,
    early_finish          DATE,
    late_start            DATE,
    late_finish           DATE,
    total_float           INT DEFAULT 0,
    free_float            INT DEFAULT 0,
    is_critical           BOOLEAN DEFAULT false,
    is_milestone          BOOLEAN DEFAULT false,
    weight_percent        DECIMAL(5,2) DEFAULT 0
                          CHECK (weight_percent BETWEEN 0 AND 100),
    contingency_days      INT DEFAULT 0,                            -- [V3] from risk linkage
    status                VARCHAR(30) DEFAULT 'not_started'
                          CHECK (status IN ('not_started','in_progress',
                                           'completed','blocked','cancelled')),
    priority              INT DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_tasks_phase   ON tasks(phase_id, status);
CREATE INDEX idx_tasks_dates   ON tasks(start_date_scheduled, end_date_scheduled);
CREATE INDEX idx_tasks_critical ON tasks(is_critical) WHERE is_critical = true;
```

#### Task Dependencies

```sql
CREATE TABLE task_dependencies (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id              UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    predecessor_task_id  UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    dependency_type      VARCHAR(2) NOT NULL DEFAULT 'FS'
                         CHECK (dependency_type IN ('FS','SS','FF','SF')),
    lag_days             INT DEFAULT 0,   -- positive = lag, negative = lead
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_no_self_loop UNIQUE (task_id, predecessor_task_id),
    CONSTRAINT chk_no_self_ref  CHECK (task_id <> predecessor_task_id)
);
CREATE INDEX idx_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_deps_pred ON task_dependencies(predecessor_task_id);
```

#### Resources

```sql
CREATE TABLE resources (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id           UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id                UUID REFERENCES users(id),   -- optional Clerk user link
    name                   VARCHAR(150) NOT NULL,
    role                   VARCHAR(100),
    hourly_rate_dh         DECIMAL(10,2) DEFAULT 0,
    monthly_capacity_hours INT DEFAULT 168,              -- 21 days × 8h
    skills                 JSONB DEFAULT '[]',
    is_active              BOOLEAN DEFAULT true,
    entry_date             DATE,
    exit_date              DATE
);
CREATE INDEX idx_resources_workspace ON resources(workspace_id, is_active);
```

#### Task Assignments

```sql
CREATE TABLE task_assignments (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id           UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    resource_id       UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    allocation_percent DECIMAL(5,2) DEFAULT 100
                      CHECK (allocation_percent BETWEEN 0 AND 100),
    planned_hours     DECIMAL(10,2),
    UNIQUE (task_id, resource_id)
);
```

#### Resource Calendars

```sql
CREATE TABLE resource_calendars (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    date        DATE NOT NULL,
    event_type  VARCHAR(20) NOT NULL CHECK (event_type IN ('holiday','leave','overtime')),
    description VARCHAR(255),
    UNIQUE (resource_id, date)
);
```

#### Progress Logs

```sql
CREATE TABLE progress_logs (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id          UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    log_date         DATE NOT NULL,
    physical_percent DECIMAL(5,2) NOT NULL
                     CHECK (physical_percent BETWEEN 0 AND 100),
    actual_hours     DECIMAL(10,2) DEFAULT 0,
    actual_cost_dh   DECIMAL(15,2) DEFAULT 0,
    logged_by        UUID REFERENCES users(id),
    notes            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (task_id, log_date)
);
CREATE INDEX idx_progress_task ON progress_logs(task_id, log_date);
```

#### Deliverables

```sql
CREATE TABLE deliverables (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id       UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    name          VARCHAR(255) NOT NULL,
    description   TEXT,
    due_date      DATE,
    status        VARCHAR(30) DEFAULT 'draft'
                  CHECK (status IN ('draft','submitted','in_review',
                                   'approved','rejected')),
    assigned_to   UUID REFERENCES users(id),
    file_url      TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_deliverables_task   ON deliverables(task_id, status);
CREATE INDEX idx_deliverables_due    ON deliverables(due_date)
                                     WHERE status NOT IN ('approved','cancelled');
```

#### Deliverable Events (Audit Trail)

```sql
CREATE TABLE deliverable_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deliverable_id  UUID NOT NULL REFERENCES deliverables(id) ON DELETE CASCADE,
    from_status     VARCHAR(30),
    to_status       VARCHAR(30) NOT NULL,
    user_id         UUID REFERENCES users(id),
    comment         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

#### Risks [V3-MUST]

```sql
CREATE TABLE risks (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id       UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title            VARCHAR(255) NOT NULL,
    description      TEXT,
    category         VARCHAR(50) NOT NULL
                     CHECK (category IN ('technical','schedule','budget',
                                        'resource','external','quality')),
    probability      INT NOT NULL CHECK (probability BETWEEN 1 AND 5),
    impact           INT NOT NULL CHECK (impact BETWEEN 1 AND 5),
    risk_score       INT GENERATED ALWAYS AS (probability * impact) STORED,
    mitigation       TEXT,
    owner_id         UUID REFERENCES users(id),
    status           VARCHAR(20) DEFAULT 'active'
                     CHECK (status IN ('active','mitigated','closed')),
    contingency_threshold INT DEFAULT 15,  -- score >= this triggers contingency
    contingency_factor    DECIMAL(5,2) DEFAULT 0.15, -- 15% duration increase
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_risks_project ON risks(project_id, status);
CREATE INDEX idx_risks_score   ON risks(risk_score DESC) WHERE status = 'active';
```

#### Risk-Task Links [V3-MUST]

```sql
CREATE TABLE risk_task_links (
    risk_id     UUID NOT NULL REFERENCES risks(id) ON DELETE CASCADE,
    task_id     UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    PRIMARY KEY (risk_id, task_id)
);
```

#### Risk Updates [V3-MUST]

```sql
CREATE TABLE risk_updates (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id    UUID NOT NULL REFERENCES risks(id) ON DELETE CASCADE,
    note       TEXT NOT NULL,
    user_id    UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Notifications [V3-SHOULD]

```sql
CREATE TABLE notifications (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type         VARCHAR(50) NOT NULL,
    title        VARCHAR(255) NOT NULL,
    message      TEXT,
    entity_type  VARCHAR(50),
    entity_id    UUID,
    is_read      BOOLEAN DEFAULT false,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_notifs_user ON notifications(user_id, is_read, created_at DESC);
```

#### Audit Logs [V3-SHOULD]

```sql
CREATE TABLE audit_logs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    user_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    entity_type  VARCHAR(50) NOT NULL,
    entity_id    UUID,
    action       VARCHAR(20) NOT NULL CHECK (action IN ('create','update','delete')),
    old_value    JSONB,
    new_value    JSONB,
    ip_address   INET,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_workspace ON audit_logs(workspace_id, created_at DESC);
CREATE INDEX idx_audit_entity    ON audit_logs(entity_type, entity_id);
```

### 5.3 Database Indexes Summary

| Index Name | Table | Columns | Purpose |
|:---|:---|:---|:---|
| `idx_projects_workspace` | projects | workspace_id, status | Workspace project listing |
| `idx_tasks_phase` | tasks | phase_id, status | Phase task listing |
| `idx_tasks_dates` | tasks | start_date_scheduled, end_date_scheduled | Gantt range queries |
| `idx_tasks_critical` | tasks | is_critical (partial) | Critical path highlighting |
| `idx_deps_task` | task_dependencies | task_id | Forward dependency traversal |
| `idx_deps_pred` | task_dependencies | predecessor_task_id | Backward dependency traversal |
| `idx_resources_workspace` | resources | workspace_id, is_active | Active resource listing |
| `idx_progress_task` | progress_logs | task_id, log_date | EVM time-series queries |
| `idx_deliverables_task` | deliverables | task_id, status | Deliverable listing |
| `idx_deliverables_due` | deliverables | due_date (partial) | Overdue detection |
| `idx_baselines_project` | project_baselines | project_id, is_active | Active baseline lookup |
| `idx_risks_project` | risks | project_id, status | Risk register listing |
| `idx_risks_score` | risks | risk_score DESC (partial) | Risk matrix sort |
| `idx_notifs_user` | notifications | user_id, is_read, created_at | Notification center |
| `idx_audit_workspace` | audit_logs | workspace_id, created_at | Audit log pagination |

---

## SECTION 6 — DETAILED DESIGN — BUSINESS ALGORITHMS {#section-6}

### 6.1 CPM Engine — Critical Path Method

The CPM engine is implemented as a **stateless Python service** (`cpm_engine.py`) that operates on in-memory data structures. It is fully decoupled from the database layer to remain independently testable.

**Input:** A list of `TaskNode` objects (id, duration_days, date constraints, list of `DependencyLink` objects with predecessor_id, dependency_type, lag_days).

**Step 1 — Topological Sort (Kahn's algorithm)**
Nodes with no predecessors are placed in the initial queue. Processing order is determined by traversing the dependency graph iteratively, removing nodes once all predecessors are resolved. Circular dependency detection: if the sort cannot resolve all nodes (queue empties before all nodes are processed), a `CircularDependencyError` is raised and the operation is rejected.

**Step 2 — Forward Pass (Early Dates)**
For each node in topological order:
- `Early Start (ES)` is the maximum of all predecessor constraints based on dependency type:
  - **FS:** `ES = max(EF(predecessor) + lag)`
  - **SS:** `ES = max(ES(predecessor) + lag)`
  - **FF:** `EF = max(EF(predecessor) + lag)` → `ES = EF - duration`
  - **SF:** `EF = max(ES(predecessor) + lag)` → `ES = EF - duration`
- For tasks with no predecessors: `ES = project start date` (or date constraint if defined).
- `Early Finish (EF) = ES + duration_days`

**Step 3 — Backward Pass (Late Dates)**
Starting from terminal nodes (no successors), traverse in reverse topological order:
- `Late Finish (LF)` is the minimum of all successor constraints:
  - **FS:** `LF = min(LS(successor) - lag)`
  - **SS:** `LS = min(LS(successor) - lag)` → `LF = LS + duration`
  - **FF:** `LF = min(LF(successor) - lag)`
  - **SF:** `LS = min(LF(successor) - lag)` → `LF = LS + duration`
- For terminal nodes: `LF = project end date` (or maximum EF if no constraint).
- `Late Start (LS) = LF - duration_days`

**Step 4 — Float Computation**
- `Total Float = LS - ES` (= `LF - EF`)
- `Free Float = ES(earliest successor) - EF(current node)`
- **Critical path:** all tasks where `Total Float = 0`. Any slip in a critical task directly extends the project end date.

**Trigger conditions:** The CPM recalculation is triggered automatically in the API layer whenever: (a) a dependency is added or removed, (b) a task duration is modified, (c) a date constraint is changed, (d) a risk contingency coefficient is applied to a task. Results are persisted to the `tasks` table (early_start, early_finish, late_start, late_finish, total_float, free_float, is_critical) and the CPM cache in Vercel KV is invalidated.

**Performance target:** < 2 seconds for a project with up to 1,000 tasks and 1,500 dependency links.

### 6.2 EVM Calculator — Earned Value Management

All EVM calculations are executed by `evm_calculator.py` as a service invoked with `(project_id, reference_date, baseline_id)`.

#### Core Formulas

| Indicator | Formula | Meaning |
|:---|:---|:---|
| **PV** | Σ(budget_task × planned_percent_at_T) | Planned Value at reference date T, interpolated from the active baseline schedule |
| **EV** | Σ(budget_task × physical_percent_actual) | Earned Value — work actually accomplished |
| **AC** | Σ(actual_cost_dh) up to reference date T | Actual Cost — real expenditure to date |
| **SPI** | EV / PV | Schedule Performance Index (< 1 = behind) |
| **CPI** | EV / AC | Cost Performance Index (< 1 = over budget) |
| **EAC** | AC + (BAC − EV) / (SPI × CPI) | Estimate at Completion — enhanced formula accounting for both schedule and cost efficiency |
| **VAC** | BAC − EAC | Variance at Completion (negative = projected overrun) |
| **TCPI** | (BAC − EV) / (BAC − AC) | To-Complete Performance Index — CPI required to finish within BAC |
| **SV** | EV − PV | Schedule Variance (< 0 = behind) |
| **CV** | EV − AC | Cost Variance (< 0 = over budget) |

*Note on EAC formula: The V3 enhanced formula `EAC = AC + (BAC − EV) / (SPI × CPI)` assumes future performance will be impacted by both schedule and cost inefficiencies simultaneously. This is more conservative than the V2 formula `EAC = BAC / CPI` which only accounts for cost efficiency.*

#### WBS Roll-up Logic

EVM metrics are computed bottom-up through the WBS hierarchy using weighted averages:
1. At the task level: raw PV, EV, AC values computed from progress logs and baseline budget.
2. At the phase level: PV, EV, AC = Σ(task values) within the phase. Phase physical percent = Σ(task_physical_percent × task_weight_percent) / Σ(task_weight_percent).
3. At the project level: same aggregation across all phases.

Edge cases: if `AC = 0` (no actual cost recorded), CPI is set to `null` (not 1.0) to avoid false reassurance. Division-by-zero guards are applied on all ratio calculations.

#### Planned Value Interpolation

For a task with baseline dates `[planned_start, planned_finish]` and a reference date T:
- If T < planned_start: planned_percent = 0%
- If T > planned_finish: planned_percent = 100%
- Otherwise: planned_percent = (T − planned_start) / (planned_finish − planned_start) × 100 (linear interpolation)

This assumes linear progress distribution within a task. The assumption is applied uniformly for simplicity; non-linear curves are a V4 enhancement.

#### Alert Thresholds (configurable per workspace)

| Condition | Default Threshold | Severity |
|:---|:---|:---|
| Schedule slip | SPI < 0.95 | Warning |
| Cost overrun | CPI < 0.90 | Warning |
| Severe schedule slip | SPI < 0.80 | Critical |
| Severe cost overrun | CPI < 0.75 | Critical |
| Resource overload | Allocated > 110% of capacity | Warning |
| Deliverable overdue | Due date passed, status ≠ Approved | Warning |
| Risk criticality breach | risk_score ≥ contingency_threshold | Warning |

### 6.3 Resource Leveling Algorithm [V3-MUST]

The resource leveling algorithm resolves over-allocations by shifting non-critical tasks forward within their available free float, without extending the project's overall end date.

**Input:** Full list of tasks with CPM results (ES, EF, LS, LF, total_float, free_float, is_critical), resource assignments with allocation percentages, resource capacity per month.

**Process:**

**Step 1 — Overload Detection**
For each resource and each time period (week or month), compute the sum of allocated hours across all active tasks. If this sum exceeds the resource's net available hours (capacity minus leave), flag the period as overloaded.

**Step 2 — Candidate Selection**
In each overloaded period, identify all non-critical tasks (`is_critical = false`) assigned to the overloaded resource. Rank candidates by descending `total_float` (most flexible tasks first — they have the most room to shift without impacting the schedule).

**Step 3 — Task Shifting**
For the highest-float candidate, compute the maximum shift distance: `max_shift = total_float - contingency_days`. Shift the task start date forward by the minimum of (max_shift, days needed to clear the overload). Deduct the shift from the task's remaining float. Recompute the affected period's allocation.

**Step 4 — Convergence Check**
Repeat Steps 2–3 for all overloaded periods. If an overload cannot be resolved (all tasks in the period are critical, or all non-critical tasks have exhausted their float), flag it as an **irresolvable overload** and include it in the leveling report without applying changes.

**Step 5 — Iteration Cap**
A maximum of 100 iterations is enforced to prevent infinite loops on pathological graphs. If the cap is reached without full convergence, partial results are returned with the remaining overloads flagged.

**Output:** Leveling report listing: (a) tasks shifted with old and new dates, (b) overloads resolved, (c) irresolvable overloads with recommended manual actions, (d) impact on total_float consumed per task. The report is a preview by default — changes are only committed to the database upon explicit PM confirmation.

### 6.4 Multi-Baselines Management [V3-MUST]

**Baseline creation:** A baseline snapshot captures the complete planning state of the project at a given point in time — all tasks with their scheduled dates, durations, weights, dependencies, resource assignments, and phase structure — serialized as a JSONB object in `project_baselines.snapshot`.

**Immutability rule:** Once created, a baseline snapshot is never modified. It is append-only. Amendments generate a new baseline (B1, B2, etc.) rather than overwriting the previous one.

**Active baseline:** Only one baseline per project can be `is_active = true` at any time. The active baseline is the reference for all PV and EVM calculations. Switching the active baseline triggers an EVM recalculation against the new reference.

**Baseline comparison:** The comparison service produces a delta report between two baselines: tasks added or removed, duration changes, date shifts (start/finish delta in days), budget changes, and weight changes. This delta is visualized as a side-by-side Gantt overlay on the frontend.

**Baseline naming convention:** B0 = initial contract baseline, B1/B2/... = contractual amendments. The version_code is user-defined but should follow the project's contract amendment numbering.

### 6.5 Risk Contingency Application [V3-MUST]

When a risk's `risk_score` reaches or exceeds its `contingency_threshold`:

1. The risk service identifies all tasks linked to this risk via `risk_task_links`.
2. For each linked task, `contingency_days` is updated: `contingency_days = ROUND(duration_days × contingency_factor)`.
3. The effective task duration for CPM purposes is computed as `duration_days + contingency_days`.
4. A CPM recalculation is triggered for the project.
5. A notification is generated for the PM: *"Risk [title] has reached criticality threshold. Contingency of X days applied to [n] linked tasks. Project end date may be affected."*

When a risk is mitigated or closed, contingency days are removed from linked tasks and CPM is recalculated.

### 6.6 AI Predictive Engine — LLM Analysis [V3-SHOULD]

**Invocation:** Asynchronous background job triggered by the PM (on-demand) or automatically at monthly period close (via QStash scheduled job). The job is non-blocking — the UI never waits for AI results.

**Input preparation:** The engine prepares a structured summary of the project's EVM data — weekly PV/EV/AC series, SPI/CPI trend over the last 8 weeks, top 5 delayed tasks with their assigned resources, deliverable status counts, active risk scores. This summary is serialized as structured JSON and injected as context into the LLM prompt.

**LLM call:** The engine calls the Anthropic API (claude-sonnet-4-20250514 model) with a system prompt defining its role as a project controls analyst. The prompt instructs the model to produce: (a) a 3-sentence executive assessment of the project's health trajectory, (b) up to 3 specific actionable recommendations, (c) identification of the highest-risk work packages with reasoning.

**Output storage:** The response is stored in a new `ai_insights` table (project_id, insight_text, generated_at, triggered_by). The PM sees the latest insight in an "AI Insights" panel on the project dashboard, with the generation timestamp and a regenerate button.

**Guardrails:** The AI module is read-only. It has no ability to modify planning data. Insights are clearly labeled as AI-generated advisory content, not authoritative conclusions.

---

## SECTION 7 — IMPLEMENTATION PLANNING {#section-7}

### 7.1 Guiding Principles — Vibe Coding Protocol

Each atomic task (🔹) in this plan is designed to be completed in a single AI-assisted coding session of 30 minutes to 2 hours. Tasks are:
- **Narrow:** One file, one service, one endpoint, or one component per task.
- **Testable:** Each task produces a verifiable output (passing test, rendered UI, functional endpoint).
- **Independent:** Tasks within a phase are as decoupled as possible to allow parallel work.

Minimum code coverage target: **85%** on the CPM engine, EVM calculator, and resource leveling service.

### 7.2 Phase Breakdown

---

#### PHASE 0 — INFRASTRUCTURE SETUP
**Deliverable:** Operational development environment, configured monorepo, CI/CD active, PostgreSQL accessible.

| # | Task |
|:---|:---|
| T0.01 | Create GitHub repository with monorepo structure (`/apps/backend`, `/apps/frontend`, `/packages/shared`) |
| T0.02 | Initialize `.gitignore`, `.editorconfig`, root `README.md`, Git branches (main / develop / feature/*) |
| T0.03 | Create Python 3.12 virtual environment and `requirements.txt` (FastAPI, SQLAlchemy 2.0, asyncpg, Alembic, Pydantic v2, python-jose, openpyxl, reportlab, anthropic, pytest, pytest-asyncio, httpx) |
| T0.04 | Create `requirements-dev.txt` (black, isort, flake8, mypy, pre-commit) and configure `pyproject.toml` |
| T0.05 | Initialize Next.js 15 with App Router and TypeScript, configure Tailwind CSS v3 |
| T0.06 | Install and initialize shadcn/ui; add base components: Button, Card, Input, Table, Dialog, Toast, Badge, Tabs |
| T0.07 | Install frontend dependencies: lucide-react, recharts, @tanstack/react-query, zustand, date-fns, clsx |
| T0.08 | Configure `tsconfig.json` with path aliases (@/components, @/lib, @/hooks, @/types) |
| T0.09 | Create Supabase (or Neon) PostgreSQL 16 instance, retrieve connection strings, test asyncpg connection |
| T0.10 | Initialize Alembic: `alembic init`, configure `alembic.ini` and `env.py` with async engine |
| T0.11 | Create Clerk application, configure email/password and Google OAuth, retrieve API keys |
| T0.12 | Install `@clerk/nextjs`, configure `ClerkProvider` in `layout.tsx`, create `middleware.ts` for route protection |
| T0.13 | Create `app/core/config.py` with `Settings` class (Pydantic BaseSettings), create `.env.example` |
| T0.14 | Create GitHub Actions workflows: `backend-ci.yml` (lint + pytest) and `frontend-ci.yml` (tsc + eslint + build) |
| T0.15 | Connect GitHub repo to Vercel, configure `vercel.json` to route `/api/*` to FastAPI, test first preview deployment |

---

#### PHASE 1 — BACKEND FOUNDATION
**Deliverable:** FastAPI application structured, all SQLAlchemy models defined, all Alembic migrations applied, database schema complete.

| # | Task |
|:---|:---|
| T1.01 | Create `app/main.py`: FastAPI instantiation, CORS middleware, API version prefix, `/health` endpoint |
| T1.02 | Create `app/core/exceptions.py`, `app/core/middleware.py` (request logging), `app/core/dependencies.py` (get_db, get_current_user) |
| T1.03 | Create `app/core/permissions.py`: `require_role()` and `require_workspace_member()` FastAPI dependencies |
| T1.04 | Create `app/core/audit.py`: `@audit_log(entity_type, action)` decorator |
| T1.05 | Create SQLAlchemy models: Workspace, User, WorkspaceMember + Alembic migration |
| T1.06 | Create SQLAlchemy models: Project, Phase + Alembic migration |
| T1.07 | Create SQLAlchemy models: Task, TaskDependency + all indexes + Alembic migration |
| T1.08 | Create SQLAlchemy models: Resource, TaskAssignment, ResourceCalendar + Alembic migration |
| T1.09 | Create SQLAlchemy models: ProgressLog, Deliverable, DeliverableEvent + Alembic migration |
| T1.10 | **[V3]** Create SQLAlchemy models: ProjectBaseline, Risk, RiskTaskLink, RiskUpdate + Alembic migration |
| T1.11 | **[V3]** Create SQLAlchemy models: Notification, AuditLog, AIInsight + Alembic migration |
| T1.12 | Create all Pydantic v2 schemas (request/response DTOs) for all entities |
| T1.13 | Create `app/api/v1/router.py`: centralized router registry; verify all models import without errors |

---

#### PHASE 2 — AUTH & WORKSPACE API
**Deliverable:** User sync from Clerk, CRUD workspaces, 4-role RBAC enforced.

| # | Task |
|:---|:---|
| T2.01 | Create `routers/webhooks.py`: POST `/webhooks/clerk` with svix-signature verification, upsert User on `user.created`, update on `user.updated` |
| T2.02 | Create `workspace_service.py`: create, get_by_id, list_by_user, update, delete, auto-generate unique slug |
| T2.03 | Create `routers/workspaces.py`: CRUD endpoints with RBAC guards applied |
| T2.04 | Create `member_service.py`: invite, update_role, remove, list_members |
| T2.05 | Create `routers/members.py`: member management endpoints; verify role guards with integration tests |

---

#### PHASE 3 — PLANNING API (WBS + DEPENDENCIES)
**Deliverable:** Full project → phase → task → dependency → assignment CRUD, WBS code auto-generation.

| # | Task |
|:---|:---|
| T3.01 | Create `project_service.py`: CRUD + stats aggregation; `routers/projects.py` with status filtering and pagination |
| T3.02 | Create `phase_service.py`: CRUD, auto-generate WBS codes (1.0, 2.0), reorder with index recalculation, weight validation |
| T3.03 | Create `task_service.py`: CRUD, hierarchical WBS codes (1.1, 1.1.1...), parent_task_id management, milestone logic |
| T3.04 | Create `dependency_service.py`: add, remove, list; DFS cycle detection before accepting any new dependency |
| T3.05 | Create `assignment_service.py`: assign resource to task with allocation%, auto-compute planned_hours, overload warning |
| T3.06 | Create `routers/planning.py`: expose all planning endpoints with proper RBAC |

---

#### PHASE 4 — CPM ENGINE
**Deliverable:** CPM algorithm fully implemented, unit-tested, integrated into API with automatic triggering.

| # | Task |
|:---|:---|
| T4.01 | Define `TaskNode`, `DependencyLink`, `CPMResult` dataclasses in `cpm_engine.py` |
| T4.02 | Implement `build_graph()`: adjacency dict from TaskNode list |
| T4.03 | Implement `topological_sort()`: Kahn's algorithm with circular dependency detection |
| T4.04 | Implement `forward_pass()`: ES/EF for all 4 dependency types (FS, SS, FF, SF) with lag support |
| T4.05 | Implement `backward_pass()`: LS/LF from terminal nodes with all dependency type formulas |
| T4.06 | Implement float computation: total_float, free_float, is_critical assignment |
| T4.07 | Create `cpm_service.py`: load tasks from DB, run CPM engine, persist results, invalidate KV cache |
| T4.08 | Create endpoint `POST /projects/{id}/cpm/recalculate`; add auto-trigger hooks in planning service |
| T4.09 | Write unit tests: simple chain, parallel merge, lag/lead, SS/FF types, circular detection |
| T4.10 | Write performance test: 1,000 tasks < 2 seconds |

---

#### PHASE 5 — RESOURCE & CAPACITY API
**Deliverable:** Resource CRUD, calendar management, workload histogram data, resource leveling algorithm.

| # | Task |
|:---|:---|
| T5.01 | Create `resource_service.py`: CRUD, optional Clerk user link, role filter, monthly cost forecast |
| T5.02 | Create `routers/resources.py`: CRUD endpoints |
| T5.03 | Create `calendar_service.py`: add/remove leave and holiday; `date_utils.py`: count_working_days() with Moroccan public holiday defaults |
| T5.04 | Create `workload_service.py`: monthly allocated vs. available hours per resource; endpoint GET /resources/{id}/workload |
| T5.05 | **[V3]** Implement `resource_leveler.py`: overload detection, candidate ranking by total_float, shift logic, irresolvable flagging, iteration cap |
| T5.06 | **[V3]** Create endpoint `POST /projects/{id}/resource-leveling` with preview mode (default) and commit mode |

---

#### PHASE 6 — EVM API
**Deliverable:** Progress log CRUD, full EVM calculation engine, S-curve data, alerts, multi-baseline management.

| # | Task |
|:---|:---|
| T6.01 | Create `progress_service.py`: CRUD with validations (0–100%, date range, no duplicate per task+date), auto-compute actual_cost_dh |
| T6.02 | Create `routers/evm.py`: progress log endpoints |
| T6.03 | Implement `evm_calculator.py`: PV interpolation, EV, AC, SPI, CPI, enhanced EAC, VAC, TCPI, WBS roll-up with division-by-zero guards |
| T6.04 | Implement S-curve generation: cumulative weekly PV, EV, AC series from baseline and progress logs |
| T6.05 | Create endpoint `GET /projects/{id}/s-curve` |
| T6.06 | Create `alert_service.py`: threshold checks, alert persistence, notification generation |
| T6.07 | Create endpoints `GET /projects/{id}/alerts` and `POST /alerts/{id}/acknowledge` |
| T6.08 | **[V3]** Implement `baseline_service.py`: create snapshot (JSONB), lock baseline, switch active baseline, compare two baselines (delta report) |
| T6.09 | **[V3]** Create endpoints `POST /projects/{id}/baselines`, `GET /projects/{id}/baselines`, `GET /baselines/{id}/compare` |
| T6.10 | Write EVM unit tests: SPI=1.0 on-schedule, CPI<1 overrun, roll-up aggregation, AC=0 edge case |

---

#### PHASE 7 — DELIVERABLES API
**Deliverable:** Deliverable CRUD, file upload, 4-state workflow state machine with audit trail.

| # | Task |
|:---|:---|
| T7.01 | Create `deliverable_service.py`: CRUD, overdue detection filter |
| T7.02 | Create `routers/deliverables.py`: CRUD endpoints with overdue and status filters |
| T7.03 | Configure Vercel Blob / S3 credentials; create `file_storage.py`: upload_file(), delete_file() |
| T7.04 | Create endpoint `POST /deliverables/{id}/upload` with file type and size validation (20 MB max) |
| T7.05 | Implement `workflow_service.py`: state machine with allowed transitions, role validation, DeliverableEvent persistence, notification generation |
| T7.06 | Create endpoint `POST /deliverables/{id}/transition` |

---

#### PHASE 8 — RISK REGISTER API [V3-MUST]
**Deliverable:** Full risk CRUD, risk-task linkage, contingency application, risk matrix data endpoint.

| # | Task |
|:---|:---|
| T8.01 | Create `risk_service.py`: CRUD, risk_score is computed column (probability × impact), status filtering |
| T8.02 | Create `routers/risks.py`: CRUD endpoints with criticality filter |
| T8.03 | Implement risk-task link service: add/remove links; contingency application logic (update task.contingency_days, trigger CPM) |
| T8.04 | Create endpoints: `POST /risks/{id}/link-task`, `DELETE /risks/{id}/link-task/{task_id}` |
| T8.05 | Create endpoint `GET /projects/{id}/risk-matrix`: risks organized by 5×5 matrix cell |
| T8.06 | Create endpoint `POST /risks/{id}/updates`: add tracking note with timestamp |

---

#### PHASE 9 — NOTIFICATIONS & AUDIT [V3-SHOULD]
**Deliverable:** Notification system, global audit trail.

| # | Task |
|:---|:---|
| T9.01 | Create `notification_service.py`: create, list (with unread count), mark_read, mark_all_read |
| T9.02 | Create `routers/notifications.py`: GET /notifications, PUT /notifications/{id}/read, PUT /notifications/read-all |
| T9.03 | Apply `@audit_log` decorator on all mutating endpoints (POST, PUT, DELETE); verify old_value / new_value capture |
| T9.04 | Create endpoint `GET /projects/{id}/audit-log` with pagination and filters (entity_type, user_id, date range) |

---

#### PHASE 10 — IMPORT / EXPORT [V3-MUST]
**Deliverable:** Native Excel import, formatted Excel export, PDF synthesis report.

| # | Task |
|:---|:---|
| T10.01 | Design and create standardized import Excel template: tabs — Project, Phases, Tasks, Resources, Dependencies |
| T10.02 | Implement `excel_importer.py`: parse with openpyxl, row-by-row validation, structured error report (row number, field, reason) |
| T10.03 | Create endpoint `POST /projects/import-excel`: upload → parse → create full project + WBS in DB; return import report |
| T10.04 | Implement `excel_exporter.py`: multi-tab workbook with openpyxl (Gantt simplified, EVM data, resource workload, deliverables), conditional formatting for SPI/CPI |
| T10.05 | Create endpoint `GET /projects/{id}/export/excel` |
| T10.06 | Implement `pdf_generator.py`: reportlab report with cover page, executive summary, KPI cards, alerts, deliverable status |
| T10.07 | Create endpoint `GET /projects/{id}/export/pdf` |

---

#### PHASE 11 — AI PREDICTIVE ENGINE [V3-SHOULD]
**Deliverable:** LLM-based predictive analysis integrated as async background job.

| # | Task |
|:---|:---|
| T11.01 | Create `ai_engine.py`: prepare structured EVM context summary (weekly series, SPI/CPI trend, delayed tasks, risk scores) |
| T11.02 | Implement Anthropic API call (claude-sonnet-4-20250514): system prompt as project controls analyst, structured output (assessment, recommendations, high-risk work packages) |
| T11.03 | Create `ai_insights` table migration; implement result storage and retrieval |
| T11.04 | Create `routers/ai.py`: `POST /projects/{id}/ai/analyze` (trigger async job), `GET /projects/{id}/ai/insights` (retrieve latest) |
| T11.05 | Configure QStash scheduled trigger for monthly auto-analysis |

---

#### PHASE 12 — FRONTEND FOUNDATION
**Deliverable:** Next.js application with layout, design system, and TanStack Query hooks.

| # | Task |
|:---|:---|
| T12.01 | Create root `app/layout.tsx`: ClerkProvider, QueryClientProvider, ToastProvider |
| T12.02 | Create `(auth)/layout.tsx` (unauthenticated) and `(app)/layout.tsx` (protected with Sidebar + Header) |
| T12.03 | Create `components/layout/Sidebar.tsx`: navigation — Dashboard, Projects, Resources, Deliverables, Risks, Settings |
| T12.04 | Create `components/layout/Header.tsx`: breadcrumb, workspace switcher, notification bell with unread badge, user avatar |
| T12.05 | Define global CSS variables: primary colors, semantic states (success/warning/danger), typography |
| T12.06 | Create base UI components: StatusBadge, KPICard, DataTable (with sort/pagination/search), PageHeader, EmptyState, LoadingSpinner, SkeletonCard |
| T12.07 | Create `lib/api/client.ts`: axios instance with Clerk token interceptor |
| T12.08 | Create all domain hooks: useProjects, useTasks, useResources, useEVM, useDeliverables, useRisks, useNotifications, useBaselines |

---

#### PHASE 13 — FRONTEND AUTH & WORKSPACES
**Deliverable:** Login/register pages, workspace selector, member management.

| # | Task |
|:---|:---|
| T13.01 | Create `(auth)/login/page.tsx` and `(auth)/register/page.tsx` with customized Clerk components |
| T13.02 | Create `workspaces/page.tsx` with WorkspaceCard and CreateWorkspaceModal |
| T13.03 | Create `settings/page.tsx`: member list, role management, InviteMemberModal |

---

#### PHASE 14 — FRONTEND PROJECT DASHBOARD
**Deliverable:** Project list, project KPI dashboard, portfolio view.

| # | Task |
|:---|:---|
| T14.01 | Create `projects/page.tsx` with ProjectCard (SPI/CPI mini, progress %, budget), status filter, CreateProjectModal |
| T14.02 | Create `projects/[id]/dashboard/page.tsx`: EVM summary cards (SPI, CPI, EAC, VAC, TCPI), progress bar, alerts panel, upcoming milestones, top delayed tasks |
| T14.03 | Create `portfolio/page.tsx`: PortfolioHealthMatrix (SPI/CPI all projects) and PortfolioBudgetSummary |
| T14.04 | Create `components/ai/AIInsightsPanel.tsx`: display latest AI insight text, generation timestamp, regenerate button **[V3]** |

---

#### PHASE 15 — FRONTEND PLANNING & GANTT
**Deliverable:** WBS editor, Gantt chart with critical path and dependencies.

| # | Task |
|:---|:---|
| T15.01 | Create `planning/page.tsx` with tabs: WBS / Gantt / Resources |
| T15.02 | Create `components/planning/WBSTree.tsx`: hierarchical tree with expand/collapse, WBS codes, milestone diamond icons |
| T15.03 | Create `components/planning/TaskRow.tsx`: columns — WBS, Name, Duration, Start, Finish, Assigned, %, Status |
| T15.04 | Create `AddTaskModal.tsx` (with parent selector) and `EditTaskModal.tsx` |
| T15.05 | Create `components/planning/DependencyManager.tsx`: add/remove dependencies with type and lag |
| T15.06 | Create `GanttChart.tsx`: SVG timeline, task bars colored by status, critical path bars in red, milestone diamonds, dependency arrows |
| T15.07 | Add Gantt zoom controls (Week / Month / Quarter), today line, EV progress overlay |
| T15.08 | Create `components/baselines/BaselinePanel.tsx`: list of baselines, active toggle, create new baseline button **[V3]** |
| T15.09 | Create `components/baselines/BaselineComparator.tsx`: side-by-side Gantt overlay comparing two baselines **[V3]** |

---

#### PHASE 16 — FRONTEND EVM & PROGRESS
**Deliverable:** S-curves, progress entry form, My Tasks view.

| # | Task |
|:---|:---|
| T16.01 | Create `SCurveChart.tsx`: Recharts LineChart with 3 series (PV blue, EV green, AC red), custom tooltip showing SPI/CPI at hovered date |
| T16.02 | Create `ProgressLogForm.tsx`: weekly entry (%, actual hours, date, notes) with validation |
| T16.03 | Create `ProgressLogHistory.tsx`: editable historical entries list |
| T16.04 | Create `my-tasks/page.tsx`: tasks assigned to the current user with quick-access progress entry |

---

#### PHASE 17 — FRONTEND RESOURCES
**Deliverable:** Resource directory, workload histogram, resource calendar.

| # | Task |
|:---|:---|
| T17.01 | Create `resources/page.tsx` with ResourceCard and AddResourceModal |
| T17.02 | Create `WorkloadHistogram.tsx`: BarChart allocated vs. capacity with utilization color coding (green / orange / red) |
| T17.03 | Create `resources/workload/page.tsx`: global workload view for all resources |
| T17.04 | Create `ResourceCalendar.tsx`: monthly calendar with leave and holidays displayed |
| T17.05 | Create resource leveling UI: trigger button, preview report modal showing shifted tasks, confirm/cancel actions **[V3]** |

---

#### PHASE 18 — FRONTEND DELIVERABLES & RISKS
**Deliverable:** Deliverable workflow interface, risk register with 5×5 matrix.

| # | Task |
|:---|:---|
| T18.01 | Create `deliverables/page.tsx` with tabs: All / Pending / Overdue / Approved |
| T18.02 | Create `DeliverableCard.tsx`, `WorkflowActions.tsx` (context-sensitive by role and status), `DeliverableTimeline.tsx` |
| T18.03 | Create `risks/page.tsx` with RiskTable (sortable by risk_score) and AddRiskModal |
| T18.04 | Create `RiskMatrix.tsx`: interactive 5×5 SVG heatmap with risks positioned by probability/impact **[V3]** |
| T18.05 | Create `RiskDetail.tsx`: linked tasks, contingency status, risk update timeline **[V3]** |

---

#### PHASE 19 — FRONTEND REPORTING & CALENDAR
**Deliverable:** Export panel, calendar view.

| # | Task |
|:---|:---|
| T19.01 | Create `ExportPanel.tsx`: Excel and PDF export buttons with period selector and loading states |
| T19.02 | Create `calendar/page.tsx` and `CalendarView.tsx`: monthly calendar showing tasks, milestones, and deliverables with type color coding **[V3]** |

---

#### PHASE 20 — TESTS & QUALITY ASSURANCE
**Deliverable:** Integration test suite, E2E tests, performance benchmarks, coverage > 85% on core engines.

| # | Task |
|:---|:---|
| T20.01 | Create `tests/integration/conftest.py`: test DB, HTTP client, test user, test workspace fixtures |
| T20.02 | Write `test_auth.py`: verify 401 on all unauthenticated requests |
| T20.03 | Write `test_projects.py`: full CRUD with field assertions |
| T20.04 | Write `test_planning.py`: create WBS + dependencies → verify CPM results |
| T20.05 | Write `test_evm.py`: progress logs → verify SPI/CPI computed correctly |
| T20.06 | Write `test_deliverables.py`: all workflow transitions, role violations |
| T20.07 | Write `test_rbac.py`: Viewer cannot create/update, Contributor cannot approve |
| T20.08 | **[V3]** Write `test_baselines.py`: create, compare, switch active baseline → verify EVM recalculation |
| T20.09 | **[V3]** Write `test_resource_leveling.py`: inject overload, verify non-critical tasks shifted, irresolvable flagged |
| T20.10 | **[V3]** Write `test_risk_contingency.py`: risk score breach → verify contingency applied → CPM recalculated |
| T20.11 | Configure `playwright.config.ts`; write E2E specs: auth flow, project creation, progress log entry, deliverable approval |
| T20.12 | Write performance benchmarks: CPM on 1,000 tasks < 2s, EVM on 1,000 logs < 3s |

---

#### PHASE 21 — PRODUCTION DEPLOYMENT
**Deliverable:** Application live on production, monitoring active, documentation complete.

| # | Task |
|:---|:---|
| T21.01 | Configure all production environment variables in Vercel dashboard |
| T21.02 | Configure custom domain; enable Vercel Analytics and Speed Insights; set up deployment alerts |
| T21.03 | Create Supabase Pro production instance; run `alembic upgrade head`; configure RLS policies on all workspace-scoped tables |
| T21.04 | Configure automated daily backups; test and document restore procedure |
| T21.05 | Create all production indexes (verify against Section 5.3 index table) |
| T21.06 | Configure Sentry (backend + frontend): DSN, 5xx error alerts, performance traces |
| T21.07 | Configure Vercel budget alerts |
| T21.08 | Verify complete Swagger/OpenAPI documentation on all endpoints |
| T21.09 | Write `CONTRIBUTING.md`: local setup, code conventions, Git workflow |
| T21.10 | Write User Manual: project onboarding, progress entry, report export |
| T21.11 | Write Operational Handbook (DEX): deployment procedure, environment variables reference, maintenance procedures |

---

### 7.3 Sprint Execution Order

| Sprint | Phases | Label | Objective |
|:---|:---|:---|:---|
| 1 | P0 → P1 → P2 | Foundations | Authenticated API, DB schema complete, CI/CD active |
| 2 | P3 → P4 + CPM tests | Planning Core | Full WBS + CPM engine operational and tested |
| 3 | P5 → P6 + EVM tests | EVM & Resources Core | Progress entry, EVM calculation, resource workload |
| 4 | P7 → P8 → P9 → P10 → P11 | V3 Modules | Deliverables, Risk Register, Notifications, Import/Export, AI Engine |
| 5 | P12 → P13 → P14 | Frontend Core | Navigable app with operational dashboards |
| 6 | P15 → P16 → P17 | Frontend Planning & EVM | Gantt + S-curves + Resource histogram |
| 7 | P18 → P19 | Frontend V3 Modules | Deliverables workflow, Risk matrix, Calendar, Export panel |
| 8 | P20 → P21 | QA & Deployment | End-to-end tested, production live, monitoring active |

---

## SECTION 8 — GOVERNANCE & DELIVERABLES MATRIX {#section-8}

### 8.1 Project Deliverables

| Phase | Primary Deliverable | Technical Content | Format |
|:---|:---|:---|:---|
| Initiation | Project Charter V3 | V3 objectives, budget governance, strategic realignment, NEXUS branding | PDF |
| Conceptual Design | Functional Specifications (SFD) | Complete user stories (E1–E4 epics), business rules (EVM formulas, dependency types, leveling logic, risk contingency) | PDF / Wiki |
| Architecture | Technical Architecture Document (TAD) | DB schema, API structure, Vercel configuration, security model, caching strategy | PDF / Wiki |
| UX/UI | Wireframes & Design System | Figma files: Gantt view, S-curve dashboard, resource histogram, risk matrix, baseline comparator | Figma |
| Build | Source Code Repository | Monorepo: FastAPI backend, Next.js frontend, Alembic migrations | Git (GitHub) |
| Build | API Documentation | Swagger/OpenAPI auto-generated by FastAPI, fully annotated | Web / JSON |
| Build | Test Plan & Results | Unit (CPM, EVM, leveling), integration (API, RBAC), E2E (Playwright), performance benchmarks | HTML / PDF |
| Deployment | Deployment Package | `vercel.json`, environment variables reference, Alembic migration scripts | Git / Vault |
| Closure | User Manual | Project onboarding guide, progress entry walkthrough, report export guide | PDF / Web |
| Closure | Operational Handbook (DEX) | Deployment procedure, maintenance routines, backup/restore procedure, incident response | PDF / Wiki |

### 8.2 Roles & Responsibilities

| Role | Responsibilities |
|:---|:---|
| **Project Sponsor** | Budget approval, strategic validation, monthly steering committee |
| **Solution Architect** | Technical architecture decisions, technology stack validation, security model |
| **Lead Backend Developer** | FastAPI/Python implementation, CPM engine, EVM calculator, resource leveling |
| **Lead Frontend Developer** | Next.js/React implementation, Gantt chart, S-curves, design system |
| **QA Engineer** | Test plan design, integration tests, E2E Playwright, performance benchmarks |
| **DevOps / CI-CD** | GitHub Actions pipelines, Vercel configuration, Supabase setup, monitoring |

### 8.3 Quality Gates

| Gate | Entry Criteria | Exit Criteria |
|:---|:---|:---|
| G1 — Architecture Review | Phase 0 complete | DDL schema validated, stack confirmed, Vercel POC deployed |
| G2 — Backend Core Review | Phases 1–4 complete | CPM tests passing, EVM tests passing, RBAC tests passing, coverage ≥ 85% on engines |
| G3 — V3 Feature Review | Phases 5–11 complete | All V3-MUST features tested: import, leveling, multi-baselines, risk contingency |
| G4 — Frontend Review | Phases 12–19 complete | All critical E2E specs passing, no blocking UI defects |
| G5 — Production Readiness | Phase 20 complete | Performance benchmarks met, Sentry active, backups verified, documentation complete |

---

## SECTION 9 — ANNEXES {#section-9}

### Annex A — Normative References

| Reference | Description | Application in NEXUS |
|:---|:---|:---|
| **PMI PMBOK 7th Edition** | Project Management Body of Knowledge | WBS structure, EVM (SPI, CPI, EAC), deliverable management |
| **PMI Practice Standard for EVM** | Earned Value Management formulas and governance | All EVM indicator formulas, S-curve methodology, baseline locking rules |
| **ISO/IEC/IEEE 12207:2017** | Software lifecycle standard | Phase structure: conceptual → basic → detailed → implementation → closure |
| **ISO/IEC 25010:2011** | Software quality model (SQuaRE) | Performance, security, maintainability, usability requirements |
| **PMBOK Risk Management** | Risk identification, scoring, and response planning | Risk register structure (probability × impact), contingency reserves |
| **FastAPI Documentation** | ASGI framework reference | Dependency injection pattern, OpenAPI generation, async handlers |
| **Next.js 15 Documentation** | App Router, RSC, caching, deployment | Frontend architecture, ISR, Server Actions |
| **Vercel Python Runtime Docs** | Serverless Python configuration | `vercel.json` setup, timeout limits, cold start mitigations |
| **Clerk Documentation** | JWT validation, RBAC, webhooks | Authentication implementation, user sync, role management |
| **PostgreSQL 16 Documentation** | RLS, indexing, JSONB, window functions | Data isolation, performance optimization, audit log storage |
| **Anthropic API Documentation** | Claude API, model capabilities | AI Predictive Engine integration (M7) |

### Annex B — EVM Quick Reference Card

| Symbol | Full Name | Formula | Target |
|:---|:---|:---|:---|
| PV | Planned Value | Budget × planned_percent_at_T | — |
| EV | Earned Value | Budget × physical_percent_actual | — |
| AC | Actual Cost | Σ actual_cost_dh to date | — |
| BAC | Budget at Completion | Total authorized budget | — |
| SV | Schedule Variance | EV − PV | ≥ 0 |
| CV | Cost Variance | EV − AC | ≥ 0 |
| SPI | Schedule Performance Index | EV / PV | ≥ 0.95 |
| CPI | Cost Performance Index | EV / AC | ≥ 0.90 |
| EAC | Estimate at Completion | AC + (BAC − EV) / (SPI × CPI) | ≤ BAC |
| VAC | Variance at Completion | BAC − EAC | ≥ 0 |
| TCPI | To-Complete Perf. Index | (BAC − EV) / (BAC − AC) | ≤ 1.10 |

### Annex C — RBAC Permission Matrix

| Action | Viewer | Contributor | PM | Admin |
|:---|:---|:---|:---|:---|
| View project data | ✅ | ✅ | ✅ | ✅ |
| Create/edit tasks | ❌ | ❌ | ✅ | ✅ |
| Enter progress logs | ❌ | ✅ (own tasks) | ✅ | ✅ |
| Submit deliverables | ❌ | ✅ (own tasks) | ✅ | ✅ |
| Approve/reject deliverables | ❌ | ❌ | ✅ | ✅ |
| Lock baseline | ❌ | ❌ | ✅ | ✅ |
| Run resource leveling | ❌ | ❌ | ✅ | ✅ |
| Manage risks | ❌ | ❌ | ✅ | ✅ |
| Trigger AI analysis | ❌ | ❌ | ✅ | ✅ |
| Manage workspace members | ❌ | ❌ | ❌ | ✅ |
| Delete project | ❌ | ❌ | ❌ | ✅ |
| View audit log | ❌ | ❌ | ✅ | ✅ |

### Annex D — Dependency Type Reference

| Type | Full Name | ES Formula (Successor) |
|:---|:---|:---|
| **FS** | Finish-to-Start | ES = max(EF(predecessor) + lag) |
| **SS** | Start-to-Start | ES = max(ES(predecessor) + lag) |
| **FF** | Finish-to-Finish | EF = max(EF(predecessor) + lag) → ES = EF − duration |
| **SF** | Start-to-Finish | EF = max(ES(predecessor) + lag) → ES = EF − duration |

*Lag is positive (delay). Lead is expressed as a negative lag value.*

### Annex E — Risk Score Matrix

| | **Impact 1** | **Impact 2** | **Impact 3** | **Impact 4** | **Impact 5** |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Probability 5** | 5 | 10 | 15 🔴 | 20 🔴 | 25 🔴 |
| **Probability 4** | 4 | 8 | 12 🟠 | 16 🔴 | 20 🔴 |
| **Probability 3** | 3 | 6 | 9 🟠 | 12 🟠 | 15 🔴 |
| **Probability 2** | 2 | 4 | 6 🟡 | 8 🟡 | 10 🟠 |
| **Probability 1** | 1 | 2 | 3 🟡 | 4 🟡 | 5 🟡 |

🔴 Critical (score ≥ 15): Contingency automatically applied to linked tasks.
🟠 High (score 8–14): Flagged on dashboard; PM attention required.
🟡 Low–Medium (score 1–7): Monitored; no automatic action.

---

*End of Document — NEXUS Master Guidelines V3.0*
*JESA S.A. — Digital Engineering & Safety Division*
*Approved for Execution — May 24, 2026*
