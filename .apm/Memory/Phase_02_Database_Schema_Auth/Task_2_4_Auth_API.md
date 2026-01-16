# Task 2.4 - User Registration & Login API

## Status
- [x] **Completed** (2026-01-16)

## Approach
1.  **Schema Updates**: 
    - Updated `backend/app/models/user.py` to include `UserCreate` and `UserRead` schemas.
    - Created `backend/app/models/auth.py` for `Token` and `TokenPayload` schemas.
2.  **Dependencies**:
    - Updated `backend/app/api/deps.py` to implement `get_current_user` with real database lookup using `get_session`.
    - Corrected `reusable_oauth2` `tokenUrl` to point to `/api/v1/auth/login`.
3.  **Auth Implementation**:
    - Created `backend/app/api/v1/auth.py` implementing `/register` and `/login`.
    - Registration creates user with default `plan_type='growth'`, `is_verified=True`.
    - Login validates credentials and returns JWT.
4.  **Integration**:
    - Mounted `auth` router in `backend/app/main.py` under `/api/v1/auth` prefix.

## Key Decisions
- **Schema Location**: Kept `User`-related schemas in `user.py` for cohesion, created separate `auth.py` for generic auth tokens.
- **Timezone**: Used `datetime.now(timezone.utc)` for consistent timestamping.
- **Verification**: Defaulted new users to `is_verified=True` to facilitate immediate access as per requirements.
- **Router Prefix**: Mounted explicitly under `/api/v1/auth` to match standard REST patterns and `tokenUrl` configuration.

## Validation
- **Manual Testing**:
    - Verified `POST /api/v1/auth/register` successfully creates a new user in PostgreSQL.
    - Verified `POST /api/v1/auth/login` successfully returns a valid Bearer token.
    - Confirmed password hashing and verification logic works.

## Next Steps
- Implement frontend UI for these endpoints (Task 2.5).
- Add stricter validation or email verification flow if needed in future.
