import json
import logging
import uuid
from typing import Dict, Optional, Any
from fastapi import WebSocket

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and Redis Pub/Sub for real-time notifications.

    This implementation uses Redis Pub/Sub to enable cross-process communication
    between Celery workers (which publish notifications) and the API server
    (which pushes messages to connected WebSocket clients).

    Architecture:
    - Celery tasks publish notifications to Redis channels: f"user:{user_id}"
    - The WebSocket endpoint subscribes to the user's Redis channel
    - Messages from Redis are forwarded to the connected WebSocket client
    """

    def __init__(self):
        # Store active WebSocket connections locally
        # Format: {user_id: {connection_id: WebSocket}}
        self.active_connections: Dict[uuid.UUID, Dict[str, WebSocket]] = {}

        # Redis client for Pub/Sub
        self._redis_client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None

    @property
    def redis_client(self) -> redis.Redis:
        """Lazy initialization of Redis client."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            logger.info("Redis client initialized for WebSocket manager")
        return self._redis_client

    def get_pubsub(self) -> redis.client.PubSub:
        """Get or create a PubSub instance."""
        if self._pubsub is None:
            self._pubsub = self.redis_client.pubsub()
        return self._pubsub

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID) -> str:
        """
        Accept a WebSocket connection and store it.

        Args:
            websocket: The WebSocket connection
            user_id: UUID of the user

        Returns:
            Connection ID for tracking
        """
        await websocket.accept()

        connection_id = str(uuid.uuid4())

        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}

        self.active_connections[user_id][connection_id] = websocket

        logger.info(f"WebSocket connected: user={user_id}, connection={connection_id}")

        return connection_id

    def disconnect(self, user_id: uuid.UUID, connection_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            user_id: UUID of the user
            connection_id: Connection identifier
        """
        if user_id in self.active_connections:
            if connection_id in self.active_connections[user_id]:
                del self.active_connections[user_id][connection_id]
                logger.info(f"WebSocket disconnected: user={user_id}, connection={connection_id}")

            # Clean up empty user entries
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_message(self, message: str, user_id: uuid.UUID, connection_id: Optional[str] = None) -> None:
        """
        Send a message to a specific user's WebSocket connections.

        Args:
            message: JSON string message to send
            user_id: UUID of the user
            connection_id: Optional specific connection to target (if None, sends to all)
        """
        if user_id not in self.active_connections:
            return

        connections_to_send = (
            {connection_id: self.active_connections[user_id][connection_id]}
            if connection_id and connection_id in self.active_connections[user_id]
            else self.active_connections[user_id]
        )

        # Send to each connection (or the specific one)
        for conn_id, websocket in list(connections_to_send.items()):
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection {conn_id}: {e}")
                # Remove dead connection
                self.disconnect(user_id, conn_id)

    async def broadcast(self, message: str) -> None:
        """
        Broadcast a message to all connected WebSocket clients.

        Args:
            message: JSON string message to send
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_message(message, user_id)

    def publish_notification(self, user_id: uuid.UUID, message: Dict[str, Any]) -> None:
        """
        Publish a notification to Redis for a specific user.

        This is called by Celery workers to send notifications to users.

        Args:
            user_id: UUID of the user to notify
            message: Dictionary containing the notification data
        """
        channel = f"user:{user_id}"
        try:
            self.redis_client.publish(
                channel,
                json.dumps(message)
            )
            logger.debug(f"Published notification to {channel}: {message.get('type', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to publish notification to Redis: {e}")

    def publish_broadcast(self, message: Dict[str, Any]) -> None:
        """
        Publish a broadcast notification to all users via Redis.

        Args:
            message: Dictionary containing the notification data
        """
        channel = "broadcast:all"
        try:
            self.redis_client.publish(
                channel,
                json.dumps(message)
            )
            logger.debug(f"Published broadcast to {channel}: {message.get('type', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to publish broadcast to Redis: {e}")

    async def listen_to_redis(self, user_id: uuid.UUID, websocket: WebSocket) -> None:
        """
        Listen to Redis Pub/Sub for a specific user and forward messages to WebSocket.

        This should be run as a background task when a WebSocket connects.

        Args:
            user_id: UUID of the user
            websocket: The WebSocket connection to send messages to
        """
        channel = f"user:{user_id}"
        pubsub = self.get_pubsub()

        try:
            pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")

            # Listen for messages
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    try:
                        # Forward to WebSocket
                        await websocket.send_text(data)
                        logger.debug(f"Forwarded Redis message to user {user_id}")
                    except Exception as e:
                        logger.error(f"Failed to forward Redis message to WebSocket: {e}")
                        break

                elif message["type"] == "unsubscribe":
                    # Connection closed
                    break

        except Exception as e:
            logger.error(f"Error in Redis listener for user {user_id}: {e}")
        finally:
            try:
                pubsub.unsubscribe(channel)
                logger.info(f"Unsubscribed from Redis channel: {channel}")
            except Exception as e:
                logger.error(f"Error unsubscribing from {channel}: {e}")

    def get_connection_count(self, user_id: Optional[uuid.UUID] = None) -> int:
        """
        Get the number of active connections.

        Args:
            user_id: Optional user ID to count connections for

        Returns:
            Number of active connections
        """
        if user_id:
            return len(self.active_connections.get(user_id, {}))
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()


def notify_user(user_id: uuid.UUID, notification_type: str, data: Dict[str, Any]) -> None:
    """
    Convenience function to send a notification to a user.

    This can be called from Celery tasks to notify users about events.

    Args:
        user_id: UUID of the user to notify
        notification_type: Type of notification (e.g., "task_update", "competitor_scraped")
        data: Additional notification data
    """
    message = {
        "type": notification_type,
        "user_id": str(user_id),
        "data": data,
        "timestamp": None  # Will be set by receiver
    }
    manager.publish_notification(user_id, message)


def broadcast_notification(notification_type: str, data: Dict[str, Any]) -> None:
    """
    Convenience function to broadcast a notification to all users.

    Args:
        notification_type: Type of notification
        data: Additional notification data
    """
    message = {
        "type": notification_type,
        "data": data,
        "timestamp": None
    }
    manager.publish_broadcast(message)


__all__ = [
    'ConnectionManager',
    'manager',
    'notify_user',
    'broadcast_notification'
]
