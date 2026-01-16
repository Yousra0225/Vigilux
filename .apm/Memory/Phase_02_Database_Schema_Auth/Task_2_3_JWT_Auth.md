# Task 2.3 - JWT Authentication & Security Logic

## Status
- [x] **Completed**

## Implementation Details
1.  **Dependencies**:
    - Installed `passlib[bcrypt]`, `python-jose[cryptography]`, `python-multipart`.
    - **Pinned `bcrypt==3.2.2`** to resolve compatibility issues with `passlib` 1.7.4 (newer versions of bcrypt remove attributes passlib relies on).

2.  **Security Module (`backend/app/core/security.py`)**:
    - Implemented `get_password_hash(password)` using bcrypt.
    - Implemented `verify_password(plain_password, hashed_password)`.
    - Implemented `create_access_token(subject, expires_delta)` for JWT generation.

3.  **FastAPI Dependencies (`backend/app/api/deps.py`)**:
    - Implemented `get_current_user` dependency.
    - Uses `OAuth2PasswordBearer` to extract the token.
    - Decodes and validates the JWT.
    - **Mock Implementation**: Currently returns a dictionary `{"id": token_data, "is_active": True}` because the database is not yet connected/queried (as per Task 2.2 status).

4.  **Configuration (`backend/app/core/config.py`)**:
    - Verified `SECRET_KEY`, `ALGORITHM` (HS256), and `ACCESS_TOKEN_EXPIRE_MINUTES` are present and used.

## Verification
- Created and ran `backend/test_security_manual.py`.
- Verified password hashing creates valid bcrypt hashes.
- Verified password verification returns True for correct password and False for incorrect.
- Verified JWT tokens are generated and correctly decoded to retrieve the subject (`sub`).

## Notes for Next Tasks
- **Task 2.4 (Auth API)**: Can now use `create_access_token` and `verify_password` to implement login endpoints.
- **Task 2.2 (Migrations)**: Once the DB schema is ready, `get_current_user` in `deps.py` should be updated to fetch the actual user from the database using the ID from the token.
