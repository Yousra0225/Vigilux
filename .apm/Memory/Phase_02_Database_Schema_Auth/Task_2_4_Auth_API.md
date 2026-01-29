# Task 2.4 - User Registration & Login API

## Status
- [x] **Completed** (2026-01-29 - Re-verified and Consolidated)

## Implementation Details
1.  **Schemas**:
    - Created `backend/app/schemas/user.py` defining `UserCreate`, `UserRead`, `UserLogin`.

2.  **Auth API (`backend/app/api/v1/auth.py`)**:
    - Implemented `POST /login`: Accepts `OAuth2PasswordRequestForm`, returns JWT.
    - Implemented `POST /register`: Accepts `UserCreate`, returns `UserRead`.
    - Handles database sessions and password hashing.

3.  **Router Integration**:
    - Updated `backend/app/main.py` to include `auth.router` under `/api/v1/auth`.

## Validation
- Validated imports and structure.
- Ready for Frontend Integration.