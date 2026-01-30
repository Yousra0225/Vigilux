# Task 5.1 - Notification Preferences API

## Overview
Implemented the backend infrastructure for user-configurable notification preferences based on event scores.

## Implementation Details

### 1. Database Model
**File:** `backend/app/models/notification_setting.py`

Created the `NotificationSetting` model with the following schema:
- `id`: UUID primary key
- `user_id`: Foreign key to user table
- `channel`: Notification channel enum (EMAIL, SMS, WEBHOOK, IN_APP)
- `min_score`: Minimum score threshold for notifications (default: 70)
- `enabled`: Boolean flag to enable/disable channel

Also updated:
- `backend/app/models/user.py` - Added relationship to `notification_settings`
- `backend/app/models/__init__.py` - Exported `NotificationSetting` and `NotificationChannel`

### 2. Schemas
**File:** `backend/app/schemas/notification.py`

Created Pydantic schemas for API validation:
- `NotificationSettingBase` - Base fields
- `NotificationSettingCreate` - For creating settings
- `NotificationSettingUpdate` - For updating settings (min_score, enabled)
- `NotificationSettingRead` - For response serialization
- `NotificationSettingsList` - For list responses

### 3. API Endpoints
**File:** `backend/app/api/v1/notifications.py`

Implemented three endpoints:

#### GET `/api/v1/users/me/notifications`
- Returns all notification settings for the current user
- Authentication: Required (via `get_current_user`)

#### PATCH `/api/v1/users/me/notifications/{channel}`
- Updates a specific notification channel setting
- Accepts: `min_score` (optional), `enabled` (optional)
- Returns: Updated setting
- Authentication: Required

#### POST `/api/v1/users/me/notifications/reset`
- Resets notification settings to defaults
- Default settings:
  - EMAIL: min_score=70, enabled=True
  - SMS: min_score=85, enabled=False
  - WEBHOOK: min_score=75, enabled=False
  - IN_APP: min_score=60, enabled=True

### 4. User Registration Integration
**File:** `backend/app/api/v1/auth.py`

Modified the `/auth/register` endpoint to initialize default notification settings for new users. Uses `session.flush()` to get the user ID before creating settings.

### 5. Router Registration
**File:** `backend/app/main.py`

Added the notifications router to the main FastAPI application:
```python
app.include_router(notifications.router, prefix=settings.API_V1_STR, tags=["notifications"])
```

## API Usage Examples

### Get Notification Settings
```bash
GET /api/v1/users/me/notifications
Authorization: Bearer <token>
```

Response:
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "channel": "email",
    "min_score": 70,
    "enabled": true
  }
]
```

### Update Notification Setting
```bash
PATCH /api/v1/users/me/notifications/email
Authorization: Bearer <token>
Content-Type: application/json

{
  "min_score": 75,
  "enabled": true
}
```

## Default Settings for New Users
| Channel  | Min Score | Enabled |
|----------|-----------|---------|
| EMAIL    | 70        | Yes     |
| SMS      | 85        | No      |
| WEBHOOK  | 75        | No      |
| IN_APP   | 60        | Yes     |

## Dependencies
- User Authentication (Task 2.4) - For `get_current_user` dependency
- Event Model (Task 3.3) - Events are scored and trigger notifications

## Success Criteria
- [x] User can update their score threshold via API
- [x] Preferences are correctly persisted in the DB
- [x] Default settings initialized on user registration
