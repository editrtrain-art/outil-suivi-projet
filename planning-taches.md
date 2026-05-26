# ANTIGRAVITY V3 — PLANNING DÉTAILLÉ DE DÉVELOPPEMENT
## Outil de Suivi de Projet Digital (Python / FastAPI / Next.js)
**Date :** 24 Mai 2026 | **Classification :** Document de Planification Exécution

---

## SECTION A — PLANNING DÉTAILLÉ D'EXÉCUTION (VIBE CODING READY)

> **Convention Vibe Coding :** Chaque tâche atomique (🔹) est conçue pour être réalisable en une seule session de coding assisté par IA (30 min – 2h). Les tâches sont indépendantes autant que possible pour permettre un développement parallèle.

---

## PHASE 0 — PRÉPARATION & INFRASTRUCTURE

### Livrable : Environnement de développement opérationnel, monorepo configuré

---

#### A0.01 — Initialisation du Monorepo
🔹 **T0.01.1** — Créer le dépôt GitHub avec structure monorepo (`/apps/backend`, `/apps/frontend`, `/packages/shared`)
🔹 **T0.01.2** — Initialiser `.gitignore`, `.editorconfig`, `README.md` racine avec description projet
🔹 **T0.01.3** — Configurer les branches Git : `main` (production), `develop` (intégration), `feature/*` (développement)

**Livrable :** Dépôt GitHub opérationnel avec structure de dossiers

---

#### A0.02 — Setup Backend Python
🔹 **T0.02.1** — Créer l'environnement virtuel Python 3.12 (`python -m venv .venv`)
🔹 **T0.02.2** — Créer `requirements.txt` avec toutes les dépendances (FastAPI, SQLAlchemy 2.0, asyncpg, Alembic, Pydantic v2, python-jose, python-multipart, aiofiles, openpyxl, reportlab, pytest, pytest-asyncio, httpx)
🔹 **T0.02.3** — Créer `requirements-dev.txt` avec outils de développement (black, isort, flake8, mypy, pre-commit)
🔹 **T0.02.4** — Installer les dépendances et vérifier l'absence de conflits de versions
🔹 **T0.02.5** — Configurer `pyproject.toml` avec les paramètres black, isort, mypy, pytest

**Livrable :** Environnement Python configuré et testé

---

#### A0.03 — Setup Frontend Next.js
🔹 **T0.03.1** — Initialiser le projet Next.js 15 avec App Router et TypeScript (`npx create-next-app@latest`)
🔹 **T0.03.2** — Installer et configurer Tailwind CSS v3 avec `tailwind.config.ts`
🔹 **T0.03.3** — Installer shadcn/ui et initialiser le design system (`npx shadcn-ui@latest init`)
🔹 **T0.03.4** — Ajouter les composants shadcn/ui de base : Button, Card, Input, Table, Dialog, Toast, Badge, Tabs
🔹 **T0.03.5** — Installer les dépendances UI : lucide-react, recharts, @tanstack/react-query, zustand, date-fns, clsx, tailwind-merge
🔹 **T0.03.6** — Configurer `tsconfig.json` avec les alias de chemins (`@/components`, `@/lib`, `@/hooks`, `@/types`)

**Livrable :** Application Next.js de base démarrable

---

#### A0.04 — Setup Base de Données
🔹 **T0.04.1** — Créer un compte Supabase (ou Neon) et initialiser une instance PostgreSQL 15
🔹 **T0.04.2** — Récupérer les chaînes de connexion (DATABASE_URL, DIRECT_URL) et les stocker dans `.env`
🔹 **T0.04.3** — Tester la connexion PostgreSQL depuis Python avec `asyncpg`
🔹 **T0.04.4** — Initialiser Alembic (`alembic init alembic`) et configurer `alembic.ini` avec `env.py`

**Livrable :** Base de données PostgreSQL accessible et Alembic prêt

---

#### A0.05 — Setup Auth (Clerk)
🔹 **T0.05.1** — Créer une application Clerk, configurer les méthodes d'auth (email/password, Google OAuth)
🔹 **T0.05.2** — Récupérer les clés API Clerk (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`)
🔹 **T0.05.3** — Installer `@clerk/nextjs` dans le frontend et configurer `ClerkProvider` dans `layout.tsx`
🔹 **T0.05.4** — Créer le middleware Next.js (`middleware.ts`) pour protéger les routes authentifiées
🔹 **T0.05.5** — Installer `PyJWT` et `httpx` côté backend pour la validation des tokens Clerk
🔹 **T0.05.6** — Configurer le webhook Clerk pour synchroniser les utilisateurs avec la base de données locale

**Livrable :** Auth fonctionnel login/logout avec protection des routes

---

#### A0.06 — Variables d'Environnement & Configuration
🔹 **T0.06.1** — Créer `.env.example` documenté avec toutes les variables requises
🔹 **T0.06.2** — Créer `app/core/config.py` avec la classe `Settings` (Pydantic BaseSettings) chargeant les variables d'environnement
🔹 **T0.06.3** — Créer `app/core/database.py` avec le moteur SQLAlchemy async et la factory de session
🔹 **T0.06.4** — Créer `.env.local` (Next.js) avec les variables frontend

**Livrable :** Configuration centralisée et sécurisée

---

#### A0.07 — CI/CD Pipeline
🔹 **T0.07.1** — Créer `.github/workflows/backend-ci.yml` : lint (flake8), format check (black), tests (pytest)
🔹 **T0.07.2** — Créer `.github/workflows/frontend-ci.yml` : type-check (tsc), lint (eslint), build (next build)
🔹 **T0.07.3** — Connecter le dépôt GitHub à Vercel et configurer les variables d'environnement Vercel
🔹 **T0.07.4** — Configurer `vercel.json` pour router les requêtes `/api/*` vers le backend FastAPI Python
🔹 **T0.07.5** — Tester un premier déploiement preview sur Vercel

**Livrable :** Pipeline CI/CD opérationnel avec déploiement automatique

---

## PHASE 1 — BACKEND FONDATION (ARCHITECTURE & MODÈLES)

### Livrable : API FastAPI structurée, modèles DB définis, migrations initiales

---

#### A1.01 — Structure du Projet FastAPI
🔹 **T1.01.1** — Créer `app/main.py` : instanciation FastAPI avec titre, version, CORS middleware
🔹 **T1.01.2** — Créer `app/core/exceptions.py` : exceptions métier personnalisées (NotFoundError, ForbiddenError, ConflictError)
🔹 **T1.01.3** — Créer `app/core/middleware.py` : middleware logging des requêtes avec timing
🔹 **T1.01.4** — Créer `app/core/dependencies.py` : `get_db()` session factory et `get_current_user()` depuis JWT Clerk
🔹 **T1.01.5** — Créer `app/api/v1/router.py` : registre centralisé de tous les routeurs
🔹 **T1.01.6** — Créer `app/utils/responses.py` : helpers pour réponses standardisées (pagination, success, error)

**Livrable :** Structure FastAPI opérationnelle avec endpoint `/health` fonctionnel

---

#### A1.02 — Modèles SQLAlchemy — Workspaces & Users
🔹 **T1.02.1** — Créer `app/domain/models/workspace.py` : modèle `Workspace` (id UUID, name, slug, settings JSONB, plan_type, timestamps)
🔹 **T1.02.2** — Créer `app/domain/models/user.py` : modèle `User` (id UUID from Clerk, email, first_name, last_name, role_global)
🔹 **T1.02.3** — Créer `app/domain/models/workspace_member.py` : modèle `WorkspaceMember` (workspace_id, user_id, role, joined_at)
🔹 **T1.02.4** — Créer la migration Alembic initiale pour ces 3 tables et l'appliquer
🔹 **T1.02.5** — Écrire les schemas Pydantic : `WorkspaceCreate`, `WorkspaceResponse`, `WorkspaceMemberResponse`

**Livrable :** Tables workspaces/users créées en DB

---

#### A1.03 — Modèles SQLAlchemy — Projets & Phases
🔹 **T1.03.1** — Créer `app/domain/models/project.py` : modèle `Project` (id, workspace_id, name, description, start_date, end_date, budget_total, status, baseline_locked_at, pm_user_id)
🔹 **T1.03.2** — Créer `app/domain/models/phase.py` : modèle `Phase` (id, project_id, name, wbs_code, order_index, weight_percent, planned_start, planned_finish)
🔹 **T1.03.3** — Créer la migration Alembic et l'appliquer
🔹 **T1.03.4** — Écrire les schemas Pydantic : `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`, `PhaseCreate`, `PhaseResponse`

**Livrable :** Tables projects/phases créées

---

#### A1.04 — Modèles SQLAlchemy — Tâches & Dépendances
🔹 **T1.04.1** — Créer `app/domain/models/task.py` : modèle `Task` (id, phase_id, parent_task_id, name, wbs_code, duration_days, dates, is_milestone, weight_percent, status, priority)
🔹 **T1.04.2** — Créer `app/domain/models/task_dependency.py` : modèle `TaskDependency` (task_id, predecessor_task_id, dependency_type, lag_days) avec contrainte anti-cycle self-loop
🔹 **T1.04.3** — Créer la migration Alembic pour tasks + task_dependencies avec tous les indexes définis en V2
🔹 **T1.04.4** — Écrire les schemas Pydantic : `TaskCreate`, `TaskUpdate`, `TaskResponse`, `DependencyCreate`, `DependencyResponse`

**Livrable :** Tables tasks/dependencies créées avec indexes

---

#### A1.05 — Modèles SQLAlchemy — Ressources
🔹 **T1.05.1** — Créer `app/domain/models/resource.py` : modèle `Resource` (id, workspace_id, user_id optionnel, name, role, hourly_rate_dh, monthly_capacity_hours, skills JSONB, is_active)
🔹 **T1.05.2** — Créer `app/domain/models/task_assignment.py` : modèle `TaskAssignment` (task_id, resource_id, allocation_percent, planned_hours)
🔹 **T1.05.3** — Créer `app/domain/models/resource_calendar.py` : modèle `ResourceCalendar` (resource_id, date, type [holiday/leave], description)
🔹 **T1.05.4** — Créer la migration Alembic et l'appliquer
🔹 **T1.05.5** — Écrire les schemas Pydantic correspondants

**Livrable :** Tables resources/assignments créées

---

#### A1.06 — Modèles SQLAlchemy — EVM & Livrables
🔹 **T1.06.1** — Créer `app/domain/models/progress_log.py` : modèle `ProgressLog` (id, task_id, log_date, physical_percent, actual_hours, actual_cost_dh, logged_by, notes)
🔹 **T1.06.2** — Créer `app/domain/models/baseline.py` : modèle `Baseline` (id, project_id, name, locked_at, locked_by, snapshot JSONB)
🔹 **T1.06.3** — Créer `app/domain/models/deliverable.py` : modèle `Deliverable` (id, task_id, name, description, due_date, status, assigned_to, file_url)
🔹 **T1.06.4** — Créer `app/domain/models/deliverable_event.py` : modèle `DeliverableEvent` (id, deliverable_id, from_status, to_status, user_id, comment, timestamp)
🔹 **T1.06.5** — Créer la migration Alembic pour ces 4 tables
🔹 **T1.06.6** — Écrire tous les schemas Pydantic correspondants

**Livrable :** Toutes les tables du schéma DB créées et migrées

---

#### A1.07 — Modèles SQLAlchemy — V3 (Risk Register & Audit Trail)
🔹 **T1.07.1** — Créer `app/domain/models/risk.py` : modèle `Risk` (id, project_id, title, description, category, probability [1-5], impact [1-5], risk_score, mitigation, owner_id, status)
🔹 **T1.07.2** — Créer `app/domain/models/audit_log.py` : modèle `AuditLog` (id, workspace_id, user_id, entity_type, entity_id, action, old_value JSONB, new_value JSONB, timestamp, ip_address)
🔹 **T1.07.3** — Créer `app/domain/models/notification.py` : modèle `Notification` (id, user_id, type, title, message, entity_type, entity_id, is_read, created_at)
🔹 **T1.07.4** — Créer la migration Alembic et l'appliquer

**Livrable :** Tables V3 (risques, audit, notifications) créées

---

## PHASE 2 — MODULE AUTH & WORKSPACES

### Livrable : API Auth complète, gestion des workspaces et membres

---

#### A2.01 — Webhook Clerk → Synchronisation Users
🔹 **T2.01.1** — Créer `app/routers/webhooks.py` : endpoint POST `/webhooks/clerk` pour recevoir les événements `user.created`, `user.updated`, `user.deleted`
🔹 **T2.01.2** — Implémenter la vérification de signature Clerk (`svix-signature`) pour sécuriser le webhook
🔹 **T2.01.3** — Implémenter l'upsert User en DB à la réception du webhook `user.created`
🔹 **T2.01.4** — Implémenter la mise à jour User à la réception du webhook `user.updated`
🔹 **T2.01.5** — Tester le webhook avec ngrok en développement local

**Livrable :** Synchronisation automatique utilisateurs Clerk → DB

---

#### A2.02 — Service & Router Workspaces
🔹 **T2.02.1** — Créer `app/domain/services/workspace_service.py` avec les méthodes : `create_workspace()`, `get_workspace_by_id()`, `get_user_workspaces()`, `update_workspace()`, `delete_workspace()`
🔹 **T2.02.2** — Créer `app/routers/workspaces.py` : endpoints CRUD (`POST /workspaces`, `GET /workspaces`, `GET /workspaces/{id}`, `PUT /workspaces/{id}`, `DELETE /workspaces/{id}`)
🔹 **T2.02.3** — Implémenter la vérification des permissions : seul l'admin du workspace peut le modifier/supprimer
🔹 **T2.02.4** — Implémenter la génération automatique du `slug` unique à partir du nom

**Livrable :** CRUD Workspaces fonctionnel

---

#### A2.03 — Gestion des Membres & RBAC
🔹 **T2.03.1** — Créer `app/domain/services/member_service.py` : `invite_member()`, `update_member_role()`, `remove_member()`, `get_workspace_members()`
🔹 **T2.03.2** — Créer `app/routers/members.py` : endpoints (`POST /workspaces/{id}/members`, `GET /workspaces/{id}/members`, `PUT /workspaces/{id}/members/{user_id}`, `DELETE /workspaces/{id}/members/{user_id}`)
🔹 **T2.03.3** — Créer `app/core/permissions.py` : décorateurs/dépendances FastAPI vérifiant le rôle (`require_role("pm")`, `require_workspace_member()`)
🔹 **T2.03.4** — Appliquer les guards RBAC sur tous les endpoints workspaces

**Livrable :** Système RBAC 4 rôles opérationnel

---

## PHASE 3 — MODULE PLANIFICATION & WBS

### Livrable : CRUD complet Projets → Phases → Tâches → Dépendances

---

#### A3.01 — Service & Router Projets
🔹 **T3.01.1** — Créer `app/domain/services/project_service.py` : `create_project()`, `get_projects_by_workspace()`, `get_project_by_id()`, `update_project()`, `delete_project()`, `get_project_stats()`
🔹 **T3.01.2** — Créer `app/routers/projects.py` : endpoints CRUD projets avec validation (date_fin > date_debut, budget > 0)
🔹 **T3.01.3** — Implémenter `GET /projects/{id}/stats` : agrégation counts (tâches, livrables, ressources) pour le dashboard
🔹 **T3.01.4** — Implémenter le filtrage et la pagination : `?status=active&page=1&size=20`

**Livrable :** CRUD Projets avec stats

---

#### A3.02 — Service & Router Phases
🔹 **T3.02.1** — Créer `app/domain/services/phase_service.py` : CRUD phases avec auto-génération du code WBS (`1.0`, `2.0`, etc.)
🔹 **T3.02.2** — Créer `app/routers/phases.py` : endpoints `GET/POST /projects/{id}/phases`, `PUT/DELETE /phases/{id}`
🔹 **T3.02.3** — Implémenter la réorganisation des phases : endpoint `PUT /phases/{id}/reorder` pour changer l'`order_index`
🔹 **T3.02.4** — Implémenter le recalcul automatique des poids relatifs (sum = 100%) à l'ajout/suppression d'une phase

**Livrable :** CRUD Phases avec gestion des poids WBS

---

#### A3.03 — Service & Router Tâches (CRUD de base)
🔹 **T3.03.1** — Créer `app/domain/services/task_service.py` : `create_task()`, `get_tasks_by_phase()`, `get_task_by_id()`, `update_task()`, `delete_task()`
🔹 **T3.03.2** — Créer `app/routers/planning.py` : endpoints tâches (`GET/POST /phases/{id}/tasks`, `GET/PUT/DELETE /tasks/{id}`)
🔹 **T3.03.3** — Implémenter la génération automatique du code WBS hiérarchique pour les tâches (`1.1`, `1.1.1`, etc.)
🔹 **T3.03.4** — Implémenter la gestion des tâches parentes (`parent_task_id`) pour le WBS à 5 niveaux
🔹 **T3.03.5** — Implémenter la logique des jalons (`is_milestone=True` → `duration_days=0`)

**Livrable :** CRUD Tâches avec structure WBS hiérarchique

---

#### A3.04 — Service & Router Dépendances
🔹 **T3.04.1** — Créer `app/domain/services/dependency_service.py` : `add_dependency()`, `remove_dependency()`, `get_task_dependencies()`, `validate_no_circular_dependency()`
🔹 **T3.04.2** — Implémenter l'algorithme de détection de cycle (DFS récursif) avant d'accepter une nouvelle dépendance
🔹 **T3.04.3** — Créer les endpoints : `POST /tasks/{id}/dependencies`, `DELETE /dependencies/{id}`, `GET /tasks/{id}/dependencies`
🔹 **T3.04.4** — Retourner une erreur explicite `409 Conflict` si la dépendance crée un cycle circulaire
🔹 **T3.04.5** — Ajouter le support des types de liens : FS (Finish-Start), SS (Start-Start), FF (Finish-Finish), SF (Start-Finish) avec lag/lead en jours

**Livrable :** Gestion des dépendances avec anti-cycle

---

#### A3.05 — Gestion des Affectations Ressources aux Tâches
🔹 **T3.05.1** — Créer `app/domain/services/assignment_service.py` : `assign_resource_to_task()`, `remove_assignment()`, `get_task_assignments()`, `get_resource_assignments()`
🔹 **T3.05.2** — Créer les endpoints : `POST /tasks/{id}/assignments`, `DELETE /assignments/{id}`, `GET /tasks/{id}/assignments`
🔹 **T3.05.3** — Implémenter le calcul automatique des `planned_hours` depuis durée × allocation%
🔹 **T3.05.4** — Implémenter la vérification de surcharge : alerter si allocation totale ressource > 100% sur une même période

**Livrable :** Affectation ressources/tâches avec détection surcharge

---

## PHASE 4 — MOTEUR CPM (CHEMIN CRITIQUE)

### Livrable : Algorithme CPM robuste, testé, déclenché automatiquement

---

#### A4.01 — Structure de Données CPM
🔹 **T4.01.1** — Créer `app/domain/services/cpm_engine.py` : définir les dataclasses `TaskNode` (id, duration_days, predecessors) et `DependencyLink` (predecessor_id, dep_type, lag_days)
🔹 **T4.01.2** — Créer `CPMResult` dataclass : `early_start`, `early_finish`, `late_start`, `late_finish`, `total_float`, `free_float`, `is_critical`
🔹 **T4.01.3** — Créer la méthode `build_graph()` : construire un graphe orienté (dict d'adjacence) depuis la liste de nœuds

**Livrable :** Structures de données CPM définies

---

#### A4.02 — Algorithme Forward Pass (Early Dates)
🔹 **T4.02.1** — Implémenter `topological_sort()` : tri topologique de Kahn sur le graphe des dépendances (gestion des nœuds sans prédécesseurs en premier)
🔹 **T4.02.2** — Implémenter `forward_pass()` : calculer `ES` et `EF` pour chaque nœud selon le type de dépendance
   - FS : ES(successeur) = max(EF(prédécesseurs) + lag)
   - SS : ES(successeur) = max(ES(prédécesseurs) + lag)
   - FF : EF(successeur) = max(EF(prédécesseurs) + lag) → ES = EF - durée
   - SF : EF(successeur) = max(ES(prédécesseurs) + lag) → ES = EF - durée
🔹 **T4.02.3** — Gérer les nœuds à contrainte de date (`date_contrainte`) qui imposent un ES minimum

**Livrable :** Calcul des Early Dates fonctionnel

---

#### A4.03 — Algorithme Backward Pass (Late Dates)
🔹 **T4.03.1** — Implémenter `backward_pass()` : à partir des nœuds finaux (sans successeurs), calculer `LS` et `LF` en remontant le graphe
🔹 **T4.03.2** — Calculer `total_float` = LS - ES = LF - EF pour chaque nœud
🔹 **T4.03.3** — Calculer `free_float` = ES(successeur_direct) - EF(courant)
🔹 **T4.03.4** — Identifier le chemin critique : toutes les tâches avec `total_float == 0`

**Livrable :** Backward pass et identification du chemin critique

---

#### A4.04 — Intégration CPM dans l'API
🔹 **T4.04.1** — Créer `app/domain/services/cpm_service.py` : méthode `run_cpm_for_project(project_id, db)` qui charge les tâches depuis DB et appelle `CPMEngine`
🔹 **T4.04.2** — Persister les résultats CPM dans les colonnes `start_date_scheduled`, `end_date_scheduled` de la table `tasks`
🔹 **T4.04.3** — Ajouter une colonne `is_critical` (boolean) à la table `tasks` via migration Alembic
🔹 **T4.04.4** — Créer l'endpoint `POST /projects/{id}/cpm/recalculate` : déclencher manuellement le recalcul CPM
🔹 **T4.04.5** — Déclencher automatiquement le recalcul CPM après : ajout/suppression dépendance, modification durée tâche, modification date contrainte

**Livrable :** CPM intégré et déclenché automatiquement

---

#### A4.05 — Tests Unitaires CPM
🔹 **T4.05.1** — Créer `tests/unit/test_cpm_engine.py` : test réseau simple (A → B → C) avec FS
🔹 **T4.05.2** — Test réseau en parallèle (A → C, B → C) : vérifier que ES(C) = max(EF(A), EF(B))
🔹 **T4.05.3** — Test avec lag positif et négatif (lead)
🔹 **T4.05.4** — Test avec dépendances SS et FF
🔹 **T4.05.5** — Test de détection de cycles circulaires : vérifier que `ValueError` est levé
🔹 **T4.05.6** — Test de performance : générer 1000 tâches, vérifier recalcul < 2 secondes

**Livrable :** Suite de tests CPM complète (couverture > 90%)

---

## PHASE 5 — MODULE RESSOURCES & CAPACITÉ

### Livrable : Gestion complète des ressources, calendriers, histogramme de charge

---

#### A5.01 — Service & Router Ressources
🔹 **T5.01.1** — Créer `app/domain/services/resource_service.py` : CRUD ressources, liaison optionnelle à un `user_id` Clerk
🔹 **T5.01.2** — Créer `app/routers/resources.py` : endpoints `GET/POST /workspaces/{id}/resources`, `GET/PUT/DELETE /resources/{id}`
🔹 **T5.01.3** — Implémenter le filtre par rôle : `GET /workspaces/{id}/resources?role=developer`
🔹 **T5.01.4** — Implémenter le calcul du coût mensuel prévisionnel d'une ressource : `hourly_rate × monthly_capacity_hours`

**Livrable :** CRUD Ressources opérationnel

---

#### A5.02 — Calendrier & Capacité des Ressources
🔹 **T5.02.1** — Créer `app/domain/services/calendar_service.py` : `add_leave_day()`, `add_holiday()`, `get_resource_calendar()`, `calculate_available_hours(resource_id, month, year)`
🔹 **T5.02.2** — Créer les endpoints : `POST /resources/{id}/calendar`, `GET /resources/{id}/calendar?month=5&year=2026`, `DELETE /calendar/{event_id}`
🔹 **T5.02.3** — Créer `app/utils/date_utils.py` : `count_working_days(start_date, end_date, resource_id)` en excluant weekends + jours de congé
🔹 **T5.02.4** — Implémenter un calendrier de jours fériés marocains par défaut (configurable par workspace)

**Livrable :** Gestion des calendriers et calcul de capacité nette

---

#### A5.03 — Calcul de Charge & Histogramme
🔹 **T5.03.1** — Créer `app/domain/services/workload_service.py` : `calculate_resource_workload(resource_id, year)` → charge mensuelle allouée vs capacité
🔹 **T5.03.2** — Implémenter l'agrégation : pour chaque mois, somme des heures planifiées sur toutes les tâches assignées à la ressource
🔹 **T5.03.3** — Créer l'endpoint `GET /resources/{id}/workload?year=2026` : retourner un array mensuel `[{month, allocated_hours, capacity_hours, overload_percent}]`
🔹 **T5.03.4** — Créer l'endpoint `GET /workspaces/{id}/workload-summary` : histogramme de charge pour toutes les ressources du workspace

**Livrable :** Données de charge prêtes pour le frontend

---

#### A5.04 — Lissage des Ressources (V3 — Resource Leveling)
🔹 **T5.04.1** — Créer `app/domain/services/resource_leveler.py` : définir le modèle de données (liste de tâches avec dates, ressources, floats)
🔹 **T5.04.2** — Implémenter l'algorithme de lissage : identifier les ressources en surcharge, décaler les tâches non-critiques dans leur float disponible
🔹 **T5.04.3** — Règle de priorité : décaler en priorité les tâches avec le plus grand float total (impact minimal sur le chemin critique)
🔹 **T5.04.4** — Créer l'endpoint `POST /projects/{id}/resource-leveling` : appliquer les suggestions ou retourner un preview
🔹 **T5.04.5** — Retourner un rapport de lissage : tâches décalées, nouvelles dates, surcharges résolues vs irréductibles

**Livrable :** Algorithme de lissage des ressources fonctionnel

---

## PHASE 6 — MODULE EVM (EARNED VALUE MANAGEMENT)

### Livrable : Calcul EVM complet, alertes, gestion des baselines

---

#### A6.01 — Service de Saisie d'Avancement
🔹 **T6.01.1** — Créer `app/domain/services/progress_service.py` : `create_progress_log()`, `get_progress_logs_by_task()`, `get_latest_progress()`, `update_progress_log()`
🔹 **T6.01.2** — Implémenter les validations métier : `physical_percent` entre 0 et 100, `log_date` ne peut pas être dans le futur > 7 jours, doublon par (task_id, log_date) interdit
🔹 **T6.01.3** — Créer les endpoints : `POST /progress-logs`, `GET /tasks/{id}/progress-logs`, `PUT /progress-logs/{id}`, `DELETE /progress-logs/{id}`
🔹 **T6.01.4** — Implémenter le calcul automatique du coût réel : `actual_cost_dh = actual_hours × resource.hourly_rate`

**Livrable :** Saisie d'avancement sécurisée

---

#### A6.02 — Moteur de Calcul EVM
🔹 **T6.02.1** — Créer `app/domain/services/evm_calculator.py` : classe `EVMCalculator` avec méthode principale `calculate(project_id, reference_date)`
🔹 **T6.02.2** — Implémenter le calcul de `PV` (Planned Value) : pour chaque tâche, interpoler l'avancement planifié à `reference_date` selon la durée et les dates planifiées
🔹 **T6.02.3** — Implémenter le calcul de `EV` (Earned Value) : `physical_percent × planned_budget_task`
🔹 **T6.02.4** — Implémenter le calcul de `AC` (Actual Cost) : agrégation des `actual_cost_dh` de tous les progress_logs jusqu'à `reference_date`
🔹 **T6.02.5** — Calculer les indicateurs dérivés : `SPI = EV/PV`, `CPI = EV/AC`, `EAC = BAC/CPI`, `VAC = BAC - EAC`, `TCPI = (BAC-EV)/(BAC-AC)`
🔹 **T6.02.6** — Implémenter le roll-up WBS : agréger EV/AC/PV de tâche → phase → projet avec pondération par poids relatif

**Livrable :** Calcul EVM complet avec roll-up WBS

---

#### A6.03 — Courbes en S — Données Historiques
🔹 **T6.03.1** — Créer `app/domain/services/s_curve_service.py` : générer les données de courbes en S (PV, EV, AC) cumulatives semaine par semaine sur la durée du projet
🔹 **T6.03.2** — Implémenter `generate_planned_curve(project_id)` : courbe PV théorique basée sur le planning de référence (baseline)
🔹 **T6.03.3** — Implémenter `generate_actual_curves(project_id)` : courbes EV et AC à partir des progress_logs historiques
🔹 **T6.03.4** — Créer l'endpoint `GET /projects/{id}/s-curve` : retourner un JSON avec les 3 séries de données pour le frontend

**Livrable :** Données courbes en S prêtes pour Recharts

---

#### A6.04 — Système d'Alertes EVM
🔹 **T6.04.1** — Créer `app/domain/services/alert_service.py` : `check_project_alerts(project_id)` → retourner liste d'alertes actives
🔹 **T6.04.2** — Implémenter les règles d'alerte : SPI < 0.95 (retard), CPI < 0.90 (dépassement budget), surcharge ressource > 110%, livrable en retard (due_date dépassé + statut ≠ Approuvé)
🔹 **T6.04.3** — Persister les alertes en DB et créer les notifications utilisateur correspondantes
🔹 **T6.04.4** — Créer l'endpoint `GET /projects/{id}/alerts` : liste des alertes actives avec sévérité (Info/Warning/Critical)
🔹 **T6.04.5** — Créer l'endpoint `POST /alerts/{id}/acknowledge` : marquer une alerte comme prise en compte

**Livrable :** Système d'alertes EVM fonctionnel

---

#### A6.05 — Gestion des Baselines (V3)
🔹 **T6.05.1** — Créer `app/domain/services/baseline_service.py` : `create_baseline()` → snapshot JSON du planning complet (tâches, dates, budgets, poids)
🔹 **T6.05.2** — Implémenter `lock_baseline(project_id, name, user_id)` : créer le snapshot et marquer le projet `baseline_locked_at`
🔹 **T6.05.3** — Implémenter `compare_baselines(baseline_id_1, baseline_id_2)` : retourner les deltas (tâches ajoutées, supprimées, dates décalées)
🔹 **T6.05.4** — Créer les endpoints : `POST /projects/{id}/baselines`, `GET /projects/{id}/baselines`, `GET /baselines/{id}/compare?with={baseline_id_2}`
🔹 **T6.05.5** — Modifier le calcul PV pour utiliser la baseline sélectionnée (par défaut : dernière baseline verrouillée)

**Livrable :** Gestion multi-baselines avec comparaison

---

#### A6.06 — Tests Unitaires EVM
🔹 **T6.06.1** — Créer `tests/unit/test_evm_calculator.py` : tester SPI=1.0 quand projet exactement on-schedule
🔹 **T6.06.2** — Tester CPI < 1.0 quand coûts réels dépassent le prévu
🔹 **T6.06.3** — Tester l'agrégation roll-up WBS (tâche → phase → projet)
🔹 **T6.06.4** — Tester le cas edge : `AC = 0` → pas de division par zéro dans CPI
🔹 **T6.06.5** — Tester `EAC` et `VAC` avec différents scénarios CPI

**Livrable :** Tests EVM couverts à > 95%

---

## PHASE 7 — MODULE LIVRABLES & WORKFLOW

### Livrable : Registre des livrables avec circuit de validation complet

---

#### A7.01 — CRUD Livrables
🔹 **T7.01.1** — Créer `app/domain/services/deliverable_service.py` : `create_deliverable()`, `get_deliverables_by_task()`, `get_project_deliverables()`, `update_deliverable()`
🔹 **T7.01.2** — Créer `app/routers/deliverables.py` : endpoints (`POST /tasks/{id}/deliverables`, `GET /projects/{id}/deliverables`, `GET/PUT/DELETE /deliverables/{id}`)
🔹 **T7.01.3** — Implémenter le filtre par statut : `GET /projects/{id}/deliverables?status=submitted&overdue=true`
🔹 **T7.01.4** — Implémenter la détection des livrables en retard : `due_date < today AND status != 'approved'`

**Livrable :** CRUD Livrables fonctionnel

---

#### A7.02 — Upload de Fichiers
🔹 **T7.02.1** — Configurer Vercel Blob (ou AWS S3) avec les credentials dans `.env`
🔹 **T7.02.2** — Créer `app/utils/file_storage.py` : méthodes `upload_file(file, filename)` → retourner URL publique, `delete_file(url)`
🔹 **T7.02.3** — Créer l'endpoint `POST /deliverables/{id}/upload` : accepter un fichier multipart, uploader en Blob/S3, mettre à jour `file_url` du livrable
🔹 **T7.02.4** — Valider le type de fichier (PDF, Word, Excel, PNG, ZIP) et la taille maximale (20 MB)

**Livrable :** Upload de fichiers fonctionnel

---

#### A7.03 — Workflow de Validation (State Machine)
🔹 **T7.03.1** — Créer `app/domain/services/workflow_service.py` : `transition_deliverable(deliverable_id, new_status, user_id, comment)` avec machine à états
🔹 **T7.03.2** — Définir les transitions autorisées : `draft → submitted` (contributeur), `submitted → in_review → approved/rejected` (PM ou Admin), `rejected → draft` (contributeur)
🔹 **T7.03.3** — Lever `ForbiddenError` si l'utilisateur n'a pas le rôle requis pour la transition demandée
🔹 **T7.03.4** — Persister chaque transition dans `DeliverableEvent` (audit trail)
🔹 **T7.03.5** — Créer l'endpoint `POST /deliverables/{id}/transition` : `{new_status, comment}` → valider et exécuter la transition
🔹 **T7.03.6** — Générer une notification pour le destinataire de chaque transition (contributeur notifié si rejeté, PM notifié si soumis)

**Livrable :** Workflow livrable avec audit trail complet

---

## PHASE 8 — MODULE REGISTRE DES RISQUES (V3)

### Livrable : Module risk management avec matrice probabilité/impact

---

#### A8.01 — CRUD Risques
🔹 **T8.01.1** — Créer `app/domain/services/risk_service.py` : CRUD risques, calcul automatique `risk_score = probability × impact`
🔹 **T8.01.2** — Créer `app/routers/risks.py` : endpoints (`GET/POST /projects/{id}/risks`, `GET/PUT/DELETE /risks/{id}`)
🔹 **T8.01.3** — Implémenter les catégories de risques : technique, planning, budget, ressources, externe, qualité
🔹 **T8.01.4** — Implémenter le filtrage par statut (`active/mitigated/closed`) et niveau de criticité (risk_score ≥ 15 = critique)

**Livrable :** CRUD Risques avec scoring

---

#### A8.02 — Rapport de la Matrice des Risques
🔹 **T8.02.1** — Créer l'endpoint `GET /projects/{id}/risk-matrix` : retourner les risques organisés par cellule de matrice 5×5
🔹 **T8.02.2** — Implémenter le suivi des risques : `POST /risks/{id}/updates` pour ajouter des notes de suivi avec date
🔹 **T8.02.3** — Calculer l'indicateur global de risque projet : moyenne pondérée des risk_scores actifs

**Livrable :** Matrice des risques exploitable

---

## PHASE 9 — MODULE NOTIFICATIONS & AUDIT TRAIL

### Livrable : Notifications in-app, audit trail système complet

---

#### A9.01 — Système de Notifications
🔹 **T9.01.1** — Créer `app/domain/services/notification_service.py` : `create_notification()`, `get_user_notifications()`, `mark_as_read()`, `mark_all_as_read()`
🔹 **T9.01.2** — Créer `app/routers/notifications.py` : endpoints (`GET /notifications`, `PUT /notifications/{id}/read`, `PUT /notifications/read-all`)
🔹 **T9.01.3** — Intégrer la création de notifications dans : workflow livrables, alertes EVM, invitation workspace

**Livrable :** Système de notifications in-app

---

#### A9.02 — Audit Trail Global
🔹 **T9.02.1** — Créer `app/core/audit.py` : décorateur `@audit_log(entity_type, action)` à apposer sur les endpoints mutants (POST, PUT, DELETE)
🔹 **T9.02.2** — Implémenter la capture `old_value` (avant) et `new_value` (après) en JSONB dans `audit_logs`
🔹 **T9.02.3** — Créer l'endpoint `GET /projects/{id}/audit-log` avec pagination et filtres (entity_type, user_id, date_range)

**Livrable :** Audit trail complet sur toutes les entités

---

## PHASE 10 — MODULE IMPORT/EXPORT (V3)

### Livrable : Import depuis Excel/CSV, export Excel/PDF

---

#### A10.01 — Import Projets depuis Excel
🔹 **T10.01.1** — Créer un template Excel standardisé (`project_import_template.xlsx`) : onglets Projet, Phases, Tâches, Ressources, Dépendances
🔹 **T10.01.2** — Créer `app/utils/excel_importer.py` : parser le fichier Excel avec `openpyxl`, valider les données, retourner des erreurs de validation détaillées par ligne
🔹 **T10.01.3** — Créer l'endpoint `POST /projects/import-excel` : upload multipart → parse → créer projet + WBS complet en DB
🔹 **T10.01.4** — Retourner un rapport d'import : entités créées, warnings, erreurs avec numéro de ligne

**Livrable :** Import Excel fonctionnel

---

#### A10.02 — Export Excel (Données Brutes)
🔹 **T10.02.1** — Créer `app/utils/excel_exporter.py` : générer un fichier Excel multi-onglets avec `openpyxl` (Gantt simplifié, EVM data, Resource workload, Deliverables)
🔹 **T10.02.2** — Appliquer la mise en forme : couleurs par statut, graphique courbes en S intégré, formatage conditionnel SPI/CPI
🔹 **T10.02.3** — Créer l'endpoint `GET /projects/{id}/export/excel` : télécharger le fichier `.xlsx`

**Livrable :** Export Excel formaté

---

#### A10.03 — Export PDF (Rapport de Synthèse)
🔹 **T10.03.1** — Créer `app/utils/pdf_generator.py` : générer un rapport PDF avec `reportlab` (page de garde, résumé exécutif, KPIs EVM, liste des alertes, statut livrables)
🔹 **T10.03.2** — Ajouter le logo workspace, numéro de rapport, date de génération
🔹 **T10.03.3** — Créer l'endpoint `GET /projects/{id}/export/pdf` : télécharger le rapport PDF mensuel

**Livrable :** Export PDF rapport de synthèse

---

## PHASE 11 — FRONTEND FONDATION (NEXT.JS)

### Livrable : Application Next.js structurée, routing configuré, composants de base

---

#### A11.01 — Layout & Navigation
🔹 **T11.01.1** — Créer `app/layout.tsx` : layout racine avec `ClerkProvider`, `QueryClientProvider`, `ToastProvider`
🔹 **T11.01.2** — Créer `app/(auth)/layout.tsx` : layout pages d'auth (login, register) centré sans sidebar
🔹 **T11.01.3** — Créer `app/(app)/layout.tsx` : layout protégé avec `Sidebar` + `Header` (workspace switcher, notifications bell, user avatar)
🔹 **T11.01.4** — Créer `components/layout/Sidebar.tsx` : navigation principale (Dashboard, Projets, Ressources, Livrables, Risques, Paramètres)
🔹 **T11.01.5** — Créer `components/layout/Header.tsx` : barre du haut avec fil d'Ariane, sélecteur workspace, cloche notifications, avatar utilisateur
🔹 **T11.01.6** — Configurer le `middleware.ts` Next.js pour rediriger vers `/login` si non authentifié

**Livrable :** Layout application avec navigation opérationnelle

---

#### A11.02 — Design System & Composants Transverses
🔹 **T11.02.1** — Définir les variables CSS globales : couleurs primaires (bleu/slate), états (success/warning/danger), typographie (Police principale + mono pour codes)
🔹 **T11.02.2** — Créer `components/ui/StatusBadge.tsx` : badge coloré pour statuts (active, draft, completed, blocked, etc.)
🔹 **T11.02.3** — Créer `components/ui/KPICard.tsx` : carte KPI avec valeur, tendance (↑↓), seuil coloré (vert/orange/rouge)
🔹 **T11.02.4** — Créer `components/ui/DataTable.tsx` : tableau avec tri, pagination, filtre de recherche (wrapper shadcn/ui Table)
🔹 **T11.02.5** — Créer `components/ui/PageHeader.tsx` : header de page avec titre, description, actions (boutons)
🔹 **T11.02.6** — Créer `components/ui/EmptyState.tsx` : composant état vide avec icône, message, CTA
🔹 **T11.02.7** — Créer `components/ui/LoadingSpinner.tsx` et `components/ui/SkeletonCard.tsx` pour les états de chargement

**Livrable :** Design system cohérent et réutilisable

---

#### A11.03 — Hooks API (TanStack Query)
🔹 **T11.03.1** — Créer `lib/api/client.ts` : instance axios/fetch avec interceptor d'authentification (injection token Clerk)
🔹 **T11.03.2** — Créer `hooks/useProjects.ts` : hooks useQuery/useMutation pour tous les endpoints projets
🔹 **T11.03.3** — Créer `hooks/useTasks.ts` : hooks pour tâches, phases, dépendances
🔹 **T11.03.4** — Créer `hooks/useResources.ts` : hooks pour ressources, workload, affectations
🔹 **T11.03.5** — Créer `hooks/useEVM.ts` : hooks pour progress logs, indicateurs EVM, courbes en S
🔹 **T11.03.6** — Créer `hooks/useDeliverables.ts` : hooks pour livrables et transitions workflow
🔹 **T11.03.7** — Créer `hooks/useNotifications.ts` : polling des notifications non lues

**Livrable :** Couche API React Query complète

---

## PHASE 12 — FRONTEND VUES AUTH & WORKSPACE

---

#### A12.01 — Pages d'Authentification
🔹 **T12.01.1** — Créer `app/(auth)/login/page.tsx` : page login avec composant Clerk `<SignIn />` personnalisé aux couleurs Antigravity
🔹 **T12.01.2** — Créer `app/(auth)/register/page.tsx` : page inscription avec `<SignUp />` Clerk
🔹 **T12.01.3** — Créer `app/(auth)/sso-callback/page.tsx` : page de callback OAuth (Google)

**Livrable :** Pages auth fonctionnelles

---

#### A12.02 — Sélecteur & Gestion des Workspaces
🔹 **T12.02.1** — Créer `app/(app)/workspaces/page.tsx` : page listant tous les workspaces de l'utilisateur avec accès rapide
🔹 **T12.02.2** — Créer `components/workspace/WorkspaceCard.tsx` : carte workspace avec nom, nombre de projets, membres
🔹 **T12.02.3** — Créer `components/workspace/CreateWorkspaceModal.tsx` : formulaire création workspace (nom, slug auto-généré)
🔹 **T12.02.4** — Créer `app/(app)/workspaces/[id]/settings/page.tsx` : paramètres workspace (membres, rôles, danger zone)
🔹 **T12.02.5** — Créer `components/workspace/InviteMemberModal.tsx` : invitation par email avec sélection de rôle

**Livrable :** Gestion des workspaces complète

---

## PHASE 13 — FRONTEND VUES PROJETS & DASHBOARD

---

#### A13.01 — Liste des Projets
🔹 **T13.01.1** — Créer `app/(app)/[workspaceId]/projects/page.tsx` : liste des projets avec filtres (statut, PM, date)
🔹 **T13.01.2** — Créer `components/project/ProjectCard.tsx` : carte projet avec KPIs rapides (SPI mini, avancement %, budget consommé)
🔹 **T13.01.3** — Créer `components/project/CreateProjectModal.tsx` : formulaire création projet (nom, dates, budget, PM assigné)
🔹 **T13.01.4** — Créer `components/project/ProjectStatusBadge.tsx` : badge coloré par statut (draft/active/on-hold/completed)

**Livrable :** Vue liste projets

---

#### A13.02 — Dashboard Projet (Vue Consolidée)
🔹 **T13.02.1** — Créer `app/(app)/[workspaceId]/projects/[id]/dashboard/page.tsx` : page principale avec layout en grille
🔹 **T13.02.2** — Créer `components/dashboard/EVMSummaryCards.tsx` : 5 cartes KPI (SPI, CPI, EAC, VAC, TCPI) avec codes couleur
🔹 **T13.02.3** — Créer `components/dashboard/ProjectProgressBar.tsx` : barre d'avancement global avec % planifié vs réel
🔹 **T13.02.4** — Créer `components/dashboard/AlertsPanel.tsx` : panneau des alertes actives avec sévérité et action acknowledge
🔹 **T13.02.5** — Créer `components/dashboard/MilestonesList.tsx` : prochains jalons avec statut (à venir / dépassé / atteint)
🔹 **T13.02.6** — Créer `components/dashboard/TopDelayedTasks.tsx` : top 5 tâches les plus en retard

**Livrable :** Dashboard projet complet

---

#### A13.03 — Dashboard Portefeuille (Multi-Projets)
🔹 **T13.03.1** — Créer `app/(app)/[workspaceId]/portfolio/page.tsx` : vue consolidée de tous les projets du workspace
🔹 **T13.03.2** — Créer `components/portfolio/PortfolioHealthMatrix.tsx` : tableau SPI/CPI de tous les projets avec codes couleur
🔹 **T13.03.3** — Créer `components/portfolio/PortfolioBudgetSummary.tsx` : budget global, consommé, prévisionnel pour l'ensemble du portefeuille

**Livrable :** Vue portefeuille multi-projets

---

## PHASE 14 — FRONTEND VUE WBS & PLANIFICATION

---

#### A14.01 — Éditeur WBS (Work Breakdown Structure)
🔹 **T14.01.1** — Créer `app/(app)/[workspaceId]/projects/[id]/planning/page.tsx` : page planning avec tabs (WBS / Gantt / Ressources)
🔹 **T14.01.2** — Créer `components/planning/WBSTree.tsx` : arbre WBS hiérarchique avec expand/collapse, icône jalon (losange), codes WBS
🔹 **T14.01.3** — Créer `components/planning/TaskRow.tsx` : ligne de tâche dans le WBS avec colonnage (WBS, Nom, Durée, Début, Fin, Responsable, %, Statut)
🔹 **T14.01.4** — Créer `components/planning/AddTaskModal.tsx` : formulaire d'ajout de tâche/sous-tâche avec sélection de parent
🔹 **T14.01.5** — Créer `components/planning/EditTaskModal.tsx` : formulaire d'édition complet d'une tâche
🔹 **T14.01.6** — Créer `components/planning/DependencyManager.tsx` : interface pour ajouter/supprimer des dépendances avec type de lien et lag

**Livrable :** Éditeur WBS interactif

---

#### A14.02 — Gantt Chart (Visualisation)
🔹 **T14.02.1** — Créer `components/planning/GanttChart.tsx` : composant Gantt SVG/Canvas avec timeline horizontale
🔹 **T14.02.2** — Afficher les barres de tâches colorées par statut, avec barres de tâches critiques en rouge
🔹 **T14.02.3** — Afficher les jalons en losange (◆) sur la timeline
🔹 **T14.02.4** — Afficher les flèches de dépendances entre tâches (lignes SVG avec pointes de flèche)
🔹 **T14.02.5** — Implémenter le zoom : vues Semaine / Mois / Trimestre avec navigation dans la timeline
🔹 **T14.02.6** — Afficher une ligne verticale "Aujourd'hui" pour situer la date courante
🔹 **T14.02.7** — Afficher la barre de progression physique (EV) en superposition sur la barre planifiée

**Livrable :** Gantt Chart interactif avec chemin critique

---

## PHASE 15 — FRONTEND COURBES EN S & EVM

---

#### A15.01 — Courbes en S Interactives
🔹 **T15.01.1** — Créer `components/evm/SCurveChart.tsx` : graphe Recharts LineChart avec 3 séries (PV bleu, EV vert, AC rouge)
🔹 **T15.01.2** — Ajouter un tooltip personnalisé affichant les 3 valeurs + SPI/CPI à la date survolée
🔹 **T15.01.3** — Ajouter une légende interactive et un sélecteur de période (3 mois / 6 mois / Tout)

**Livrable :** Courbes en S interactives

---

#### A15.02 — Saisie d'Avancement
🔹 **T15.02.1** — Créer `components/evm/ProgressLogForm.tsx` : formulaire de saisie hebdomadaire (% avancement, heures réelles, date, notes)
🔹 **T15.02.2** — Créer `components/evm/ProgressLogHistory.tsx` : historique des saisies avec possibilité d'édition
🔹 **T15.02.3** — Créer la vue "Mes Tâches" : `app/(app)/[workspaceId]/my-tasks/page.tsx` avec les tâches assignées à l'utilisateur connecté et accès rapide à la saisie

**Livrable :** Interface de saisie d'avancement

---

## PHASE 16 — FRONTEND RESSOURCES

---

#### A16.01 — Référentiel Ressources
🔹 **T16.01.1** — Créer `app/(app)/[workspaceId]/resources/page.tsx` : liste des ressources avec filtres (rôle, actif/inactif)
🔹 **T16.01.2** — Créer `components/resources/ResourceCard.tsx` : carte ressource avec avatar, rôle, taux horaire, capacité mensuelle
🔹 **T16.01.3** — Créer `components/resources/AddResourceModal.tsx` : formulaire ajout ressource (nom, rôle, taux DH/h, capacité, liaison user Clerk)

**Livrable :** Référentiel ressources

---

#### A16.02 — Histogramme de Charge
🔹 **T16.02.1** — Créer `components/resources/WorkloadHistogram.tsx` : BarChart Recharts avec barres allouées vs ligne de capacité maximum
🔹 **T16.02.2** — Coloriser les barres : vert (< 80%), orange (80-100%), rouge (> 100% = surcharge)
🔹 **T16.02.3** — Créer `components/resources/WorkloadSummaryTable.tsx` : tableau mensuel de charge par ressource
🔹 **T16.02.4** — Créer `app/(app)/[workspaceId]/resources/workload/page.tsx` : vue globale de charge de toutes les ressources

**Livrable :** Histogramme de charge interactif

---

#### A16.03 — Calendrier Ressource
🔹 **T16.03.1** — Créer `components/resources/ResourceCalendar.tsx` : vue calendrier mensuelle avec jours de congé et fériés colorisés
🔹 **T16.03.2** — Créer `components/resources/AddLeaveModal.tsx` : formulaire ajout congé/absence (date, type, description)

**Livrable :** Gestion calendrier ressource

---

## PHASE 17 — FRONTEND LIVRABLES & RISQUES

---

#### A17.01 — Registre des Livrables
🔹 **T17.01.1** — Créer `app/(app)/[workspaceId]/projects/[id]/deliverables/page.tsx` : liste avec tabs (Tous / En attente / En retard / Approuvés)
🔹 **T17.01.2** — Créer `components/deliverables/DeliverableCard.tsx` : carte avec nom, statut, date cible, responsable, lien fichier
🔹 **T17.01.3** — Créer `components/deliverables/WorkflowActions.tsx` : boutons d'action contextuels selon rôle et statut (Soumettre / Approuver / Rejeter + champ commentaire)
🔹 **T17.01.4** — Créer `components/deliverables/DeliverableTimeline.tsx` : historique des transitions avec qui/quand/commentaire

**Livrable :** Interface livrables avec workflow visuel

---

#### A17.02 — Matrice des Risques
🔹 **T17.02.1** — Créer `app/(app)/[workspaceId]/projects/[id]/risks/page.tsx` : page registre des risques
🔹 **T17.02.2** — Créer `components/risks/RiskMatrix.tsx` : grille 5×5 SVG affichant les risques positionnés par probabilité/impact
🔹 **T17.02.3** — Créer `components/risks/RiskTable.tsx` : tableau des risques avec tri par risk_score
🔹 **T17.02.4** — Créer `components/risks/AddRiskModal.tsx` : formulaire ajout risque (titre, catégorie, probabilité, impact, mitigation, propriétaire)

**Livrable :** Module risk management complet

---

## PHASE 18 — FRONTEND REPORTING & EXPORT

---

#### A18.01 — Interface d'Export
🔹 **T18.01.1** — Créer `components/reporting/ExportPanel.tsx` : panneau avec boutons d'export (Excel, PDF) et sélecteur de période
🔹 **T18.01.2** — Implémenter le download client-side : appeler l'endpoint API et déclencher le téléchargement du blob
🔹 **T18.01.3** — Ajouter un état de chargement durant la génération du rapport (spinner + message)

**Livrable :** Interface d'export fonctionnelle

---

#### A18.02 — Vue Calendrier (V3)
🔹 **T18.02.1** — Créer `app/(app)/[workspaceId]/projects/[id]/calendar/page.tsx` : vue calendrier mensuel
🔹 **T18.02.2** — Créer `components/planning/CalendarView.tsx` : afficher les tâches, jalons et livrables sur un calendrier mensuel avec codes couleur

**Livrable :** Vue calendrier des événements projet

---

## PHASE 19 — TESTS & ASSURANCE QUALITÉ

### Livrable : Suite de tests complète, couverture > 80%

---

#### A19.01 — Tests d'Intégration API (Backend)
🔹 **T19.01.1** — Créer `tests/integration/conftest.py` : fixtures (base de données de test, client HTTP, utilisateur test, workspace test)
🔹 **T19.01.2** — Créer `tests/integration/test_auth.py` : tester que les endpoints non-auth retournent 401
🔹 **T19.01.3** — Créer `tests/integration/test_projects.py` : CRUD complet projets avec assertions sur tous les champs
🔹 **T19.01.4** — Créer `tests/integration/test_planning.py` : créer WBS + dépendances → vérifier résultat CPM
🔹 **T19.01.5** — Créer `tests/integration/test_evm.py` : créer progress logs → vérifier SPI/CPI calculés correctement
🔹 **T19.01.6** — Créer `tests/integration/test_deliverables.py` : tester toutes les transitions du workflow
🔹 **T19.01.7** — Créer `tests/integration/test_rbac.py` : vérifier que les rôles Viewer ne peuvent pas créer/modifier

**Livrable :** Suite de tests intégration backend

---

#### A19.02 — Tests End-to-End (Playwright)
🔹 **T19.02.1** — Configurer `playwright.config.ts` avec les URLs de test et les credentials de test
🔹 **T19.02.2** — Écrire `e2e/auth.spec.ts` : login → accès workspace → logout
🔹 **T19.02.3** — Écrire `e2e/project-creation.spec.ts` : créer projet → ajouter phases → ajouter tâches → vérifier WBS
🔹 **T19.02.4** — Écrire `e2e/progress-log.spec.ts` : saisir avancement → vérifier KPIs mis à jour sur dashboard
🔹 **T19.02.5** — Écrire `e2e/deliverable-workflow.spec.ts` : soumettre → approuver → vérifier statut

**Livrable :** Tests E2E couvrant les flows critiques

---

#### A19.03 — Tests de Performance CPM
🔹 **T19.03.1** — Créer `tests/performance/test_cpm_load.py` : générer 500 tâches avec dépendances, mesurer temps de calcul CPM (cible < 2s)
🔹 **T19.03.2** — Créer `tests/performance/test_evm_load.py` : générer 1000 progress_logs, mesurer temps d'agrégation EVM (cible < 3s)

**Livrable :** Benchmarks de performance validés

---

## PHASE 20 — DÉPLOIEMENT PRODUCTION

### Livrable : Application déployée en production sur Vercel + monitoring

---

#### A20.01 — Configuration Vercel Production
🔹 **T20.01.1** — Configurer toutes les variables d'environnement production dans le dashboard Vercel
🔹 **T20.01.2** — Configurer les domaines custom (`antigravity.app` ou sous-domaine JESA)
🔹 **T20.01.3** — Activer Vercel Analytics et Speed Insights
🔹 **T20.01.4** — Configurer les alertes de déploiement (Slack ou email)

**Livrable :** Configuration Vercel production

---

#### A20.02 — Base de Données Production
🔹 **T20.02.1** — Créer l'instance PostgreSQL production sur Supabase (plan Pro)
🔹 **T20.02.2** — Appliquer toutes les migrations Alembic en production (`alembic upgrade head`)
🔹 **T20.02.3** — Configurer les règles Row-Level Security (RLS) sur Supabase pour les tables sensibles
🔹 **T20.02.4** — Configurer les backups automatiques quotidiens et tester la procédure de restauration
🔹 **T20.02.5** — Créer les indexes de production selon le schéma V2 (toutes les colonnes JOIN et WHERE fréquents)

**Livrable :** Base de données production sécurisée

---

#### A20.03 — Monitoring & Observabilité
🔹 **T20.03.1** — Configurer Sentry (backend + frontend) : DSN, alertes erreurs 5xx, traces de performance
🔹 **T20.03.2** — Créer un dashboard Sentry avec les métriques clés : error rate, p95 latency, apdex
🔹 **T20.03.3** — Configurer des alertes budget Vercel pour éviter les dépassements

**Livrable :** Stack de monitoring opérationnel

---

#### A20.04 — Documentation Finale
🔹 **T20.04.1** — Documenter l'API complète via Swagger UI auto-généré par FastAPI (vérifier que tous les endpoints ont des descriptions)
🔹 **T20.04.2** — Rédiger le `CONTRIBUTING.md` : setup local, conventions de code, workflow Git
🔹 **T20.04.3** — Rédiger le Manuel Utilisateur : onboarding nouveau projet, saisie d'avancement, export rapport
🔹 **T20.04.4** — Rédiger le Dossier d'Exploitation (DEX) : déploiement, variables d'env, procédures de maintenance

**Livrable :** Documentation complète

---

## SECTION B — SYNTHÈSE DES LIVRABLES PAR PHASE

| Phase | Nom | Livrables Clés |
|:---|:---|:---|
| **P0** | Préparation & Setup | Repo GitHub, Env Dev, DB, Auth, CI/CD |
| **P1** | Backend Fondation | Tous modèles SQLAlchemy, Migrations DB, Structure FastAPI |
| **P2** | Auth & Workspaces | API Auth, CRUD Workspaces, RBAC 4 rôles |
| **P3** | Planification & WBS | API Projets, Phases, Tâches, Dépendances, Affectations |
| **P4** | Moteur CPM | CPM Engine testé, intégré, déclenché automatiquement |
| **P5** | Ressources & Capacité | API Ressources, Calendriers, Workload, Resource Leveling |
| **P6** | EVM | Calcul SPI/CPI/EAC, Courbes en S, Alertes, Baselines |
| **P7** | Livrables & Workflow | Registre livrables, Upload fichiers, State machine 4 états |
| **P8** | Registre Risques | CRUD risques, Matrice 5×5, Scoring |
| **P9** | Notifications & Audit | Notifications in-app, Audit trail complet |
| **P10** | Import/Export | Import Excel, Export Excel formaté, Export PDF |
| **P11** | Frontend Fondation | Layout, Design System, Hooks API TanStack Query |
| **P12** | Frontend Auth & WS | Pages login, Sélecteur workspace, Gestion membres |
| **P13** | Frontend Dashboard | Dashboard projet KPIs, Portefeuille multi-projets |
| **P14** | Frontend Planning | WBS éditeur, Gantt avec chemin critique |
| **P15** | Frontend EVM | Courbes en S, Formulaire saisie avancement |
| **P16** | Frontend Ressources | Référentiel, Histogramme charge, Calendrier |
| **P17** | Frontend Livrables & Risques | Interface workflow, Matrice des risques |
| **P18** | Frontend Reporting | Export panel, Vue calendrier |
| **P19** | Tests & QA | Tests intégration, E2E Playwright, Benchmarks |
| **P20** | Déploiement | Vercel prod, DB prod, Monitoring, Documentation |

---

## SECTION C — ORDRE D'EXÉCUTION RECOMMANDÉ (VIBE CODING SPRINTS)

### Sprint 1 — Fondations
P0 complet → P1 complet → P2 complet
> Objectif : API authentifiée fonctionnelle, DB configurée, CI/CD actif

### Sprint 2 — Noyau Planning
P3 complet → P4 complet (CPM) → Tests unitaires CPM
> Objectif : Créer un projet avec WBS complet et calcul CPM opérationnel

### Sprint 3 — Noyau EVM & Ressources
P5 complet → P6 complet → Tests unitaires EVM
> Objectif : Saisie d'avancement et calcul EVM opérationnel

### Sprint 4 — Modules Complémentaires
P7 complet → P8 complet → P9 complet → P10 complet
> Objectif : Livrables, risques, notifications, imports/exports

### Sprint 5 — Frontend Core
P11 complet → P12 complet → P13 complet
> Objectif : Application navigable avec dashboards opérationnels

### Sprint 6 — Frontend Planning & EVM
P14 complet → P15 complet → P16 complet
> Objectif : Gantt + Courbes en S + Histogramme charge affichés

### Sprint 7 — Frontend Secondaire & QA
P17 complet → P18 complet → P19 complet
> Objectif : Application testée end-to-end

### Sprint 8 — Déploiement & Lancement
P20 complet
> Objectif : Application en production avec monitoring actif

---

*Document préparé pour la planification du projet Antigravity V3*
*Basé sur l'analyse comparative des Master Guidelines V1 et V2*
*JESA S.A. — Division Safety & Digital Engineering*
