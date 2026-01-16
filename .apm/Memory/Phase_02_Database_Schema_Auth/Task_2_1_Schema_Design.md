---
agent: Agent_Data_IA
task_ref: Task 2.1
status: Completed
ad_hoc_delegation: false
compatibility_issues: false
important_findings: false
---

# Task Log: Task 2.1 - PostgreSQL Schema Design

## Summary
Designed a robust relational schema for Vigilux including `users`, `projects`, `competitors`, and `events` tables, covering all requirements for tiered plans, workspace management, and competitor tracking.

## Details
1.  **Analyzed Requirements**:
    *   Confirmed need for hierarchical structure: User -> Projects -> Competitors -> Events.
    *   Defined Enums for `plan_type`, `tracking_status`, and `event_type` to ensure data integrity.
    *   Selected UUIDs for all primary keys to ensure scalability and security.

2.  **Schema Definition**:
    *   Created detailed table specifications with column names, data types, and constraints.
    *   Established foreign key relationships to maintain referential integrity.

## Output
### Schema Definition

#### 1. Table `users`
*   **Purpose**: Stores user account information, authentication details, and subscription status.
*   **Columns**:
    *   `id`: `UUID` (Primary Key, Default: `uuid_generate_v4()`)
    *   `email`: `VARCHAR(255)` (Unique, Not Null, Indexed)
    *   `hashed_password`: `VARCHAR` (Not Null)
    *   `plan_type`: `VARCHAR` / `ENUM('starter', 'growth', 'ultimate')` (Default: 'growth', Not Null)
    *   `trial_start_date`: `TIMESTAMP` (Nullable, defaults to creation time if on trial)
    *   `is_verified`: `BOOLEAN` (Default: `false`)
    *   `created_at`: `TIMESTAMP` (Default: `NOW()`)
    *   `updated_at`: `TIMESTAMP` (Default: `NOW()`, on update `NOW()`)

#### 2. Table `projects`
*   **Purpose**: Represents a workspace or a specific domain a user is monitoring.
*   **Columns**:
    *   `id`: `UUID` (Primary Key, Default: `uuid_generate_v4()`)
    *   `user_id`: `UUID` (Foreign Key -> `users.id`, On Delete: `CASCADE`, Not Null)
    *   `url`: `VARCHAR(2048)` (Not Null, the user's website)
    *   `description`: `TEXT` (Nullable)
    *   `created_at`: `TIMESTAMP` (Default: `NOW()`)

#### 3. Table `competitors`
*   **Purpose**: Entities tracked within a project.
*   **Columns**:
    *   `id`: `UUID` (Primary Key, Default: `uuid_generate_v4()`)
    *   `project_id`: `UUID` (Foreign Key -> `projects.id`, On Delete: `CASCADE`, Not Null)
    *   `name`: `VARCHAR(255)` (Not Null)
    *   `url`: `VARCHAR(2048)` (Nullable)
    *   `score`: `INTEGER` (Default: 0, Represents global threat score)
    *   `tracking_status`: `VARCHAR` / `ENUM('active', 'archived')` (Default: 'active', Not Null)
    *   `created_at`: `TIMESTAMP` (Default: `NOW()`)

#### 4. Table `events`
*   **Purpose**: Significant market signals or actions taken by competitors.
*   **Columns**:
    *   `id`: `UUID` (Primary Key, Default: `uuid_generate_v4()`)
    *   `competitor_id`: `UUID` (Foreign Key -> `competitors.id`, On Delete: `CASCADE`, Not Null)
    *   `event_type`: `VARCHAR` / `ENUM('price', 'feature', 'health', 'new_entrant')` (Not Null)
    *   `description`: `TEXT` (Not Null)
    *   `score`: `INTEGER` (Not Null, Impact score 1-10)
    *   `timestamp`: `TIMESTAMP` (Default: `NOW()`, Date of the event)

## Issues
None

## Next Steps
Implement the schema using SQLAlchemy models and alembic migrations (Task 2.2).
