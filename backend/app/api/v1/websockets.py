import json
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from app.core.config import settings
from app.models.user import User
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_user_from_token(token: str) -> User | None:
    """
    Validate JWT token and retrieve user.

    Args:
        token: JWT token from query parameter

    Returns:
        User object if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        # Import here to avoid circular dependency
        from sqlmodel import select

        from app.core.db import get_session
        from app.models.user import User

        with next(get_session()) as session:
            statement = select(User).where(User.id == uuid.UUID(user_id))
            user = session.exec(statement).first()
            return user

    except (JWTError, ValueError):
        return None


@router.websocket("/notifications/{user_id}")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: str,
    token: Annotated[str, Query(description="JWT authentication token")]
) -> None:
    """
    WebSocket endpoint for real-time notifications.

    This endpoint:
    1. Authenticates the user via JWT token in query parameter
    2. Establishes a WebSocket connection
    3. Subscribes to Redis Pub/Sub for user-specific notifications
    4. Forwards messages from Redis to the WebSocket client

    Usage:
        - Connect to: ws://localhost:8000/api/v1/notifications/{user_id}?token={jwt_token}
        - Receive real-time updates about task progress, competitor changes, etc.

    Args:
        websocket: The WebSocket connection
        user_id: UUID of the user (path parameter for identification)
        token: JWT token for authentication (query parameter)
    """
    await _handle_websocket_connection(websocket, user_id, token)


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications_alias(
    websocket: WebSocket,
    user_id: str,
    token: Annotated[str, Query(description="JWT authentication token")]
) -> None:
    """
    WebSocket endpoint alias for real-time notifications.

    This is an alias for /notifications/{user_id} at the /ws/ path.
    Both endpoints provide identical functionality.

    Usage:
        - Connect to: ws://localhost:8000/api/v1/ws/notifications/{user_id}?token={jwt_token}
        - Receive real-time updates about task progress, competitor changes, etc.

    Args:
        websocket: The WebSocket connection
        user_id: UUID of the user (path parameter for identification)
        token: JWT token for authentication (query parameter)
    """
    await _handle_websocket_connection(websocket, user_id, token)


async def _handle_websocket_connection(
    websocket: WebSocket,
    user_id: str,
    token: str
) -> None:
    """
    Shared WebSocket connection handler.

    Handles the common logic for WebSocket connection setup and management.

    Args:
        websocket: The WebSocket connection
        user_id: UUID of the user (path parameter for identification)
        token: JWT token for authentication (query parameter)
    """
    # Validate user_id format
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"Invalid user_id format: {user_id}")
        return

    # Authenticate user
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"WebSocket authentication failed for user_id: {user_id}")
        return

    # Verify the authenticated user matches the requested user_id
    if user.id != user_uuid:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"WebSocket user mismatch: {user.id} != {user_uuid}")
        return

    # Accept the connection and register with manager
    connection_id = await manager.connect(websocket, user_uuid)

    # Send initial connection message
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "connection_id": connection_id,
            "user_id": str(user_uuid),
            "message": "WebSocket connection established"
        }))
    except (RuntimeError, ConnectionError, OSError, TypeError, ValueError) as exc:
        logger.error(f"Failed to send connection message: {exc}")
        manager.disconnect(user_uuid, connection_id)
        return

    logger.info(f"WebSocket connection established for user {user_uuid} (conn: {connection_id})")

    try:
        # Listen for messages from Redis in background
        # This will block until the connection is closed
        await manager.listen_to_redis(user_uuid, websocket)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected by client: user={user_uuid}, conn={connection_id}")
    except (RuntimeError, ConnectionError, OSError) as exc:
        logger.error(f"WebSocket error for user {user_uuid}: {exc}")
    finally:
        # Clean up connection
        manager.disconnect(user_uuid, connection_id)
        logger.info(f"WebSocket connection cleaned up: user={user_uuid}, conn={connection_id}")


@router.get("/ws/status")
def websocket_status() -> dict:
    """
    Get WebSocket connection statistics.

    Returns:
        Dictionary with connection count and status
    """
    return {
        "active_connections": manager.get_connection_count(),
        "status": "operational"
    }


__all__ = ['router']
