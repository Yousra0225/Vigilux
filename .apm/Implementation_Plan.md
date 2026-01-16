# Vigilux – APM Implementation Plan
**Memory Strategy:** Dynamic-MD
**Last Modification:** Plan creation by the Setup Agent.
**Project Overview:** Vigilux is a proactive AI-driven competitive intelligence SaaS. It transforms passive monitoring into actionable "Breakthrough Signals" (Features, Prices, Financial Health, New Entrants). The platform features a global radar for market discovery and surgical tracking for selected competitors, with tiered access (Starter, Growth, Ultimate), a modern Next.js/FastAPI stack, and full Dockerization.

## Phase 1: Foundation & Infrastructure

### Task 1.1 – Monorepo Structure & Basic Boilerplates - Agent_DevOps
**Objective:** Establish the project's root structure and initialize package managers.
**Output:** Folder structure and initialization files.
**Guidance:** Ensure all directories follow the discussed monorepo pattern.

- Create backend/, frontend/, and infra/ directories.
- Initialize package.json in frontend and requirements.txt/pyproject.toml in backend.
- Set up root-level .gitignore and basic README.md.

### Task 1.2 – Docker & Docker Compose Configuration - Agent_DevOps
**Objective:** Containerize the application for consistent local development.
**Output:** Dockerfiles and docker-compose.yml.
**Guidance:** **Depends on: Task 1.1 Output**
1. Create backend/Dockerfile using a Python 3.11+ base image.
2. Create frontend/Dockerfile using a Node.js base image.
3. Create root docker-compose.yml including PostgreSQL 15+, api, and web services.
4. Configure health checks for the database to ensure it's ready before the API starts.

### Task 1.3 – GitHub Actions CI Pipeline Setup - Agent_DevOps
**Objective:** Automate quality checks (Linting & Testing).
**Output:** .github/workflows/ci.yml.
**Guidance:** **Depends on: Task 1.4 Output by Agent_Backend_Core, Task 1.5 Output by Agent_Frontend_Core**
- Define linting jobs using Ruff/Black for Python and ESLint/Prettier for JS/TS.
- Set up a test job that runs Pytest and Vitest.
- Configure triggers for push and pull requests on main and develop branches.

### Task 1.4 – Base FastAPI Setup & Clean Architecture Skeleton - Agent_Backend_Core
**Objective:** Initialize the backend with a scalable architecture.
**Output:** FastAPI boilerplate with domain-driven structure.
**Guidance:** **Depends on: Task 1.1 Output by Agent_DevOps**
1. Install FastAPI, Uvicorn, and Pydantic.
2. Create app/ structure: api/, core/ (config, security), models/, services/, and repositories/.
3. Implement a basic health-check endpoint (/health).
4. Configure CORS to allow local frontend access.

### Task 1.5 – Base Next.js Setup & Tailwind Configuration - Agent_Frontend_Core
**Objective:** Initialize the frontend with modern UI tools.
**Output:** Next.js project with Tailwind CSS.
**Guidance:** **Depends on: Task 1.1 Output by Agent_DevOps**
- Initialize Next.js with TypeScript in the frontend/ folder.
- Install and configure Tailwind CSS and Shadcn/UI (if applicable).
- Create a basic homepage with a placeholder for the Dark/Light mode toggle.

## Phase 2: Database Schema & Authentication

### Task 2.1 – PostgreSQL Schema Design - Agent_Data_IA
**Objective:** Design a robust relational schema for Vigilux.
**Output:** SQL schema definition or ERD description.
**Guidance:** **Depends on: Task 1.2 Output by Agent_DevOps**
- Define 'users' table (UUID, email, hashed_password, plan_type, trial_start_date, is_verified).
- Define 'projects' table (UUID, user_id, url, description, created_at).
- Define 'competitors' table (UUID, project_id, name, url, score, tracking_status).
- Define 'events' table (UUID, competitor_id, event_type, description, score, timestamp).

### Task 2.2 – SQLAlchemy Integration & Migrations - Agent_Backend_Core
**Objective:** Set up ORM and database migration system.
**Output:** Database models and Alembic configuration.
**Guidance:** **Depends on: Task 2.1 Output by Agent_Data_IA**
1. Configure database connection using SQLAlchemy and SQLModel.
2. Translate the schema design into Python models.
3. Initialize Alembic and generate the initial migration script.

### Task 2.3 – JWT Authentication & Security Logic - Agent_Backend_Core
**Objective:** Implement secure user authentication.
**Output:** Security utilities and FastAPI dependencies.
**Guidance:** **Depends on: Task 1.4 Output**
- Implement password hashing using passlib (bcrypt).
- Create JWT token generation (access/refresh) and validation logic.
- Implement a 'get_current_user' dependency to protect API routes.

### Task 2.4 – User Registration & Login API - Agent_Backend_Core
**Objective:** Provide endpoints for user onboarding and access.
**Output:** /auth/register and /auth/login endpoints.
**Guidance:** **Depends on: Task 2.2 Output, Task 2.3 Output**
1. Create Pydantic schemas for auth requests and responses.
2. Implement registration logic (default plan='growth', trial_start_date=now(), is_verified=True).
3. Implement login login verifying credentials and returning JWT.
4. Add error handling for duplicate emails or invalid credentials.

### Task 2.5 – Auth UI & Protected Routes - Agent_Frontend_Core
**Objective:** Create the user interface for authentication.
**Output:** Login/Register pages and auth protection logic.
**Guidance:** **Depends on: Task 2.4 Output by Agent_Backend_Core**
1. Build Register and Login forms with validation and Tailwind styling.
2. Implement client-side auth state management (localStorage/Cookies).
3. Create a ProtectedRoute component to shield dashboard pages.
4. Add basic feedback (toasts) for login success/failure.

## Phase 3: Core Business Logic & Data Mocks

### Task 3.1 – Data Seeder Script (Fixtures) - Agent_Data_IA
**Objective:** Populate the database with test data for development and demos.
**Output:** backend/app/db/seed.py script.
**Guidance:** **Depends on: Task 2.2 Output by Agent_Backend_Core**
- Create users for Starter, Growth, and Ultimate plans.
- Generate mock competitors and historical events for each user.
- Include diverse event types and scores to test filtering logic.

### Task 3.2 – Tier & Quota Management Logic - Agent_Backend_Core
**Objective:** Enforce plan-based restrictions and trial logic.
**Output:** Quota service and route dependencies.
**Guidance:** **Depends on: Task 2.4 Output**
- Define Pricing Constants: Starter (0€), Growth (49€), Ultimate (199€).
- Implement `get_effective_plan(user)`: returns 'starter' if Growth trial (>7 days) expired and unpaid.
- Define constants for competitor limits (3, 15, 50).
- Implement logic to block adding competitors beyond the limit.

### Task 3.3 – Mock IA Scoring Engine - Agent_Backend_Business
**Objective:** Simulate AI-driven analysis of market changes.
**Output:** Scoring service module.
**Guidance:** **Depends on: Task 1.4 Output by Agent_Backend_Core**
- Implement a mock scoring function (1-10) for competitor events.
- Flag events with Score > 7 as "Breakthrough Signals".
- Categorize events (Price, Feature, Health, Entry).

### Task 3.4 – Competitor Tracking & Radar API - Agent_Backend_Business
**Objective:** Provide endpoints for managing competitors and market discovery.
**Output:** /competitors and /radar endpoints.
**Guidance:** **Depends on: Task 3.2 Output by Agent_Backend_Core, Task 3.3 Output**
1. Implement CRUD for competitors (Add, List, Archive, Delete).
2. Implement 'Radar' search endpoint returning mock market data.
3. Ensure 'Archive' status stops active tracking logic simulation.
4. Add filters for Score, Status, and Date.

### Task 3.5 – Dashboard Statistics API - Agent_Backend_Business
**Objective:** Aggregate data for the frontend dashboard.
**Output:** /dashboard/stats endpoint.
**Guidance:** **Depends on: Task 2.2 Output by Agent_Backend_Core**
- Calculate summary stats (Total active, breakthroughs today, average threat).
- Group events by day for timeline charts.
- Return structured JSON compatible with frontend chart libraries.

## Phase 4: Dashboard & UI Implementation

### Task 4.1 – Layout & Navigation Shell - Agent_Frontend_Core
**Objective:** Build the application's core frame.
**Output:** MainLayout, Sidebar, and Header components.
**Guidance:** **Depends on: Task 1.5 Output**
1. Implement Dark/Light mode toggle using next-themes.
2. Create a responsive Sidebar with navigation links.
3. Build the Header showing current project and user profile.
4. Set up the MainLayout wrapper with responsive constraints.

### Task 4.2 – Dashboard Overview Page - Agent_Frontend_App
**Objective:** Create the main stats and visualization page.
**Output:** Dashboard page with charts and cards.
**Guidance:** **Depends on: Task 4.1 Output by Agent_Frontend_Core, Task 3.5 Output by Agent_Backend_Business**
1. Build reusable StatCard components.
2. Integrate Recharts to display the 'Threat Timeline'.
3. Fetch and display data from the /dashboard/stats endpoint.

### Task 4.3 – Competitor List & Timeline View - Agent_Frontend_App
**Objective:** Visualize followed competitors and their activity.
**Output:** Competitors page and Timeline component.
**Guidance:** **Depends on: Task 4.1 Output by Agent_Frontend_Core, Task 3.4 Output by Agent_Backend_Business**
1. Create a filterable table/grid for competitors.
2. Build a vertical Timeline component for events.
3. Highlight 'Breakthrough Signals' (Score > 7) with distinct styling.

### Task 4.4 – Quick View Modal & Details - Agent_Frontend_App
**Objective:** Allow rapid inspection of competitor details.
**Output:** QuickViewModal component.
**Guidance:** **Depends on: Task 4.3 Output, Task 3.4 Output by Agent_Backend_Business**
- Create a modal triggered by clicking a competitor.
- Implement lazy-loading for detailed competitor data.
- Display mock insights: Pitch, CA estimate, Strengths/Weaknesses.

### Task 4.5 – Global Radar & Discovery UI - Agent_Frontend_App
**Objective:** UI for market-wide competitive search.
**Output:** Radar page.
**Guidance:** **Depends on: Task 4.1 Output by Agent_Frontend_Core, Task 3.4 Output by Agent_Backend_Business**
1. Create a search interface to trigger the Radar scan.
2. Display results with 'Score de Menace' and action to 'Add to Dashboard'.
3. Implement 'Blurred/Locked' state for Radar results if user is on effective Starter plan.
4. Implement UI blocks/CTAs for upgrade (Growth 49€/Ultimate 199€) on locked items.

## Phase 5: Notifications & Integrations

### Task 5.1 – Notification Preferences API - Agent_Backend_Business
**Objective:** Manage user notification settings.
**Output:** /users/me/notifications endpoint.
**Guidance:** **Depends on: Task 2.4 Output by Agent_Backend_Core**
1. Create 'notification_settings' table (user_id, channel, min_score, enabled).
2. Implement GET and PATCH endpoints for preferences.
3. Initialize default settings on user registration.

### Task 5.2 – Notification Dispatcher Service - Agent_Backend_Business
**Objective:** Centralize notification logic.
**Output:** Notification dispatcher module.
**Guidance:** **Depends on: Task 5.1 Output**
- Implement logic to check event score against user threshold.
- Route notifications to enabled channels (Email, Slack, etc.).
- Simulate dispatch via console logging for the prototype.

### Task 5.3 – Multi-Channel Integration (Mock) - Agent_Backend_Business
**Objective:** Implement external communication logic.
**Output:** Slack/Discord/Email provider stubs.
**Guidance:** **Depends on: Task 5.2 Output**
- Implement mock Slack/Discord webhook callers.
- Implement mock Email sender (console log).
- Ensure Ultimate-only channels (WhatsApp/SMS) are restricted.

### Task 5.4 – Notification Settings UI - Agent_Frontend_Core
**Objective:** Interface for configuring alerts.
**Output:** Settings/Notifications page.
**Guidance:** **Depends on: Task 4.1 Output, Task 5.1 Output by Agent_Backend_Business**
1. Build toggle switches for each notification channel.
2. Implement inputs for Webhook URLs and phone numbers.
3. Add a score threshold selector (Slider or Select).

## Phase 6: QA & Finalization

### Task 6.1 – Backend Testing & Coverage - Agent_Backend_Core
**Objective:** Ensure backend reliability and performance.
**Output:** Pytest suite with coverage reports.
**Guidance:** **Depends on: Task 3.4 Output by Agent_Backend_Business**
1. Set up Pytest, Coverage.py, and FactoryBoy.
2. Write unit tests for core services (Auth, Quotas, Scoring).
3. Implement integration tests for critical API endpoints.
4. Target > 75% code coverage.

### Task 6.2 – Frontend Testing & Coverage - Agent_Frontend_Core
**Objective:** Ensure UI stability and correct state handling.
**Output:** Vitest/Jest suite.
**Guidance:** **Depends on: Task 4.3 Output by Agent_Frontend_App, Task 5.4 Output**
1. Set up Vitest and React Testing Library.
2. Write unit tests for reusable UI components.
3. Implement integration tests for the authentication and settings flows.

### Task 6.3 – E2E Scenario Implementation - Agent_DevOps
**Objective:** Validate full user journeys across all plans.
**Output:** Playwright test suite.
**Guidance:** **Depends on: Task 6.1 Output by Agent_Backend_Core, Task 6.2 Output by Agent_Frontend_Core**
1. Initialize Playwright in the monorepo root.
2. Script 2 scenarios per profile (Starter/Growth/Ultimate) covering Onboarding, Dashboard, and Radar.
3. Verify plan restrictions (locked features/quotas) are enforced in the UI.

### Task 6.4 – Technical Documentation & Installation - Agent_DevOps
**Objective:** Facilitate project handoff and deployment.
**Output:** README.md and /docs directory.
**Guidance:** **Depends on: Task 1.1 Output**
- Write a detailed README.md with Docker Compose instructions.
- Document API endpoints (via Swagger/OpenAPI).
- Add an architecture overview and troubleshooting guide in /docs.

### Task 6.5 – Final Polish & Demo Prep - Agent_DevOps
**Objective:** Ensure the prototype is production-ready and demo-capable.
**Output:** Cleaned-up repository and demo fixtures.
**Guidance:** **Depends on: Phase 5 Output by various agents**
- Perform a final linting/formatting sweep.
- Verify that seeding scripts create a visually compelling demo state.
- Conduct a final manual walkthrough of all user journeys.
