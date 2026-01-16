# Vigilux – APM Memory Root
**Memory Strategy:** Dynamic-MD
**Project Overview:** Vigilux is a proactive AI-driven competitive intelligence SaaS. It transforms passive monitoring into actionable "Breakthrough Signals" (Features, Prices, Financial Health, New Entrants). The platform features a global radar for market discovery and surgical tracking for selected competitors, with tiered access (Starter, Growth, Ultimate), a modern Next.js/FastAPI stack, and full Dockerization.

## Phase 01 – Foundation & Infrastructure Summary
*   **Outcome:** Successfully established the project foundation. The monorepo structure is set with a FastAPI backend (Clean Architecture) and Next.js frontend (Tailwind/TypeScript). Docker containerization acts as the dev/prod runtime for API, Web, and PostgreSQL services. A GitHub Actions CI pipeline is configured for linting and testing both stacks.
*   **Involved Agents:** Agent_DevOps, Agent_Backend_Core, Agent_Frontend_Core.
*   **Logs:**
    *   [.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_1_Monorepo_Structure.md](.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_1_Monorepo_Structure.md)
    *   [.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_2_Docker_Config.md](.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_2_Docker_Config.md)
    *   [.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_3_CI_Pipeline.md](.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_3_CI_Pipeline.md)
    *   [.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_4_FastAPI_Setup.md](.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_4_FastAPI_Setup.md)
    *   [.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_5_Nextjs_Setup.md](.apm/Memory/Phase_01_Foundation_Infrastructure/Task_1_5_Nextjs_Setup.md)

## Phase 02 – Database Schema & Authentication Summary
*   **Outcome:** Implemented a full-stack authentication system and database layer. PostgreSQL schema is live via Alembic/SQLModel. Backend provides JWT-based register/login endpoints with password hashing. Frontend features Login/Register pages and route protection logic integrated with the API.
*   **Involved Agents:** Agent_Data_IA, Agent_Backend_Core, Agent_Frontend_Core.
*   **Logs:**
    *   [.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_1_Schema_Design.md](.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_1_Schema_Design.md)
    *   [.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_2_SQLAlchemy_Migrations.md](.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_2_SQLAlchemy_Migrations.md)
    *   [.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_3_JWT_Auth.md](.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_3_JWT_Auth.md)
    *   [.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_4_Auth_API.md](.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_4_Auth_API.md)
    *   [.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_5_Auth_UI.md](.apm/Memory/Phase_02_Database_Schema_Auth/Task_2_5_Auth_UI.md)