# Task 5.2 - Notification Dispatcher Service

## Overview
Implemented the `NotificationService` that evaluates events against user preferences and dispatches notifications through appropriate channels.

## Implementation Details

### 1. Notification Service
**File:** `backend/app/services/notifications.py`

Created a `NotificationService` class with the following methods:

#### `get_user_notification_settings(session, user_id)`
Retrieves all notification settings for a given user from the database.

#### `dispatch_notification(session, user_id, event)`
Main method that:
1. Fetches user's notification preferences
2. Checks if the event has a score (skips if None)
3. Iterates through each notification setting
4. For enabled channels where `event.score >= setting.min_score`, sends a notification

#### `_send_notification(channel, event, score)`
Simulates sending a notification by:
1. Logging to the Python logger
2. Printing to console with format: `[NOTIF][{CHANNEL}] [{URGENCY}] Event detected! Type: {type}, Score: {score}/100 - {description}`

Urgency levels based on score:
- Score >= 90: CRITICAL
- Score >= 75: HIGH
- Score >= 60: MEDIUM
- Score < 60: LOW

#### `dispatch_bulk_notifications(session, user_ids, event)`
Helper method to dispatch the same event to multiple users.

### 2. Service Export
**File:** `backend/app/services/__init__.py`

Updated to export `NotificationService` alongside `ScoringService` and `QuotaService`.

## Notification Flow

```
Event Created
    ↓
Event Scored (ScoringService)
    ↓
NotificationService.dispatch_notification(user_id, event)
    ↓
Fetch user preferences
    ↓
For each channel setting:
    if enabled AND event.score >= min_score:
        _send_notification(channel, event, score)
    ↓
Console output: [NOTIF][CHANNEL] [URGENCY] ...
```

## Example Console Output

When a high-scoring event is detected:
```
[NOTIF][EMAIL] [HIGH] Event detected! Type: PRICE, Score: 80/100 - Competitor decreased pricing by 20%
[NOTIF][IN_APP] [HIGH] Event detected! Type: PRICE, Score: 80/100 - Competitor decreased pricing by 20%
```

Critical event (score >= 90):
```
[NOTIF][EMAIL] [CRITICAL] Event detected! Type: HEALTH, Score: 95/100 - Competitor experienced major downtime
```

## Integration Points

### With Event Creation
The service is designed to be called after event creation:
```python
# After creating and scoring an event
event.score = ScoringService.calculate_score(event_type, description)
session.add(event)
session.commit()

# Dispatch notifications
NotificationService.dispatch_notification(session, user_id, event)
```

### With Competitor Monitoring
When monitoring detects a significant competitor change:
1. Create Event
2. Score the event using `ScoringService`
3. Call `NotificationService.dispatch_notification()` for relevant users

## Supported Notification Channels

| Channel    | Description                              | Default Min Score | Default Enabled |
|------------|------------------------------------------|-------------------|-----------------|
| EMAIL      | Email notifications                      | 70                | Yes             |
| SMS        | SMS notifications                        | 85                | No              |
| WEBHOOK    | Webhook notifications                    | 75                | No              |
| IN_APP     | In-app notifications                     | 60                | Yes             |

## Dependencies
- User Preferences (Task 5.1) - Reads `NotificationSetting` from database
- Scoring Service (Task 3.3) - Expects events with `score` attribute
- Event Model - Uses `Event.type`, `Event.description`, `Event.score`

## Success Criteria
- [x] Service takes an Event and checks score against user preferences
- [x] Routes notifications to active channels
- [x] Simulates sending with console logs
- [x] Creating a high-score event triggers console log notification

## Future Enhancements
- Replace console logs with actual email sending (SMTP, SendGrid)
- Implement SMS sending (Twilio)
- Implement webhook calls
- Implement in-app notification storage
- Add notification queue for async processing
- Add rate limiting per channel
- Add notification history tracking
