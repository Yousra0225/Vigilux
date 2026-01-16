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

## Phase 03 – Core Business Logic & Data Mocks Summary
*   **Outcome:** Developed the core intelligence engine and plan enforcement logic. Implemented an AI-scoring simulator, multi-tier quota management, and a comprehensive data seeder for development. Delivered high-value API endpoints for competitor management, market radar, and dashboard analytics.
*   **Involved Agents:** Agent_Data_IA, Agent_Backend_Core, Agent_Backend_Business.
*   **Logs:**
    *   [.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_1_Data_Seeder.md](.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_1_Data_Seeder.md)
    *   [.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_2_Quota_Management.md](.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_2_Quota_Management.md)
    *   [.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_3_IA_Scoring.md](.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_3_IA_Scoring.md)
    *   [.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_4_Competitor_Radar_API.md](.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_4_Competitor_Radar_API.md)
    *   [.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_5_Dashboard_Stats_API.md](.apm/Memory/Phase_03_Core_Logic_Mocks/Task_3_5_Dashboard_Stats_API.md)

## Phase 04 – Dashboard & UI Implementation Summary
*   **Outcome:** Delivered a fully responsive and functional dashboard UI. Key features include an analytics overview with Recharts, a detailed competitor management list with activity timelines, and an AI-powered global radar. Implemented plan-aware UI logic (feature blurring) and seamless navigation shell with theme support.
*   **Involved Agents:** Agent_Frontend_Core, Agent_Frontend_App.
*   **Logs:**
    *   [.apm/Memory/Phase_04_Dashboard_UI/Task_4_1_Layout_Nav.md](.apm/Memory/Phase_04_Dashboard_UI/Task_4_1_Layout_Nav.md)
    *   [.apm/Memory/Phase_04_Dashboard_UI/Task_4_2_Dashboard_Page.md](.apm/Memory/Phase_04_Dashboard_UI/Task_4_2_Dashboard_Page.md)
    *   [.apm/Memory/Phase_04_Dashboard_UI/Task_4_3_Competitor_Timeline.md](.apm/Memory/Phase_04_Dashboard_UI/Task_4_3_Competitor_Timeline.md)
    *   [.apm/Memory/Phase_04_Dashboard_UI/Task_4_4_QuickView_Modal.md](.apm/Memory/Phase_04_Dashboard_UI/Task_4_4_QuickView_Modal.md)
    *   [.apm/Memory/Phase_04_Dashboard_UI/Task_4_5_Radar_UI.md](.apm/Memory/Phase_04_Dashboard_UI/Task_4_5_Radar_UI.md)

## Phase 05 – Notifications & Integrations Summary
*   **Outcome:** Built a comprehensive multi-channel notification system. Implemented user preference management for alerts with customizable score thresholds. Developed a centralized dispatcher that normalizes AI scores and routes notifications to Email, Slack, Discord, and WhatsApp. Enforced tiered access restrictions for premium notification channels.
*   **Involved Agents:** Agent_Backend_Business, Agent_Frontend_Core.
*   **Logs:**
    *   [.apm/Memory/Phase_05_Notifications_Integrations/Task_5_1_Notif_Prefs_API.md](.apm/Memory/Phase_05_Notifications_Integrations/Task_5_1_Notif_Prefs_API.md)
    *   [.apm/Memory/Phase_05_Notifications_Integrations/Task_5_2_Notif_Dispatcher.md](.apm/Memory/Phase_05_Notifications_Integrations/Task_5_2_Notif_Dispatcher.md)
    *   [.apm/Memory/Phase_05_Notifications_Integrations/Task_5_3_Notif_Mock_Channels.md](.apm/Memory/Phase_05_Notifications_Integrations/Task_5_3_Notif_Mock_Channels.md)
    *   [.apm/Memory/Phase_05_Notifications_Integrations/Task_5_4_Notif_Settings_UI.md](.apm/Memory/Phase_05_Notifications_Integrations/Task_5_4_Notif_Settings_UI.md)
