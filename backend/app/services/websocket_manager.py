import asyncio
import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

import redis
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

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
    - Each user gets their own PubSub instance to avoid cross-talk
    - Blocking Redis calls run in a thread pool executor to avoid blocking the event loop
    """

    def __init__(self):
        # Store active WebSocket connections locally
        # Format: {user_id: {connection_id: WebSocket}}
        self.active_connections: dict[uuid.UUID, dict[str, WebSocket]] = {}

        # Redis client for Pub/Sub
        self._redis_client: redis.Redis | None = None

        # Thread pool executor for blocking Redis operations
        self._executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="redis_pubsub")

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

    def _create_pubsub_for_user(self, user_id: uuid.UUID) -> redis.client.PubSub:
        """
        Create a new PubSub instance for a specific user.

        Each user needs their own PubSub instance because Redis PubSub
        connections can only be subscribed to one set of channels at a time.

        Args:
            user_id: UUID of the user

        Returns:
            A new PubSub instance for this user
        """
        pubsub = self.redis_client.pubsub()
        channel = f"user:{user_id}"
        pubsub.subscribe(channel)
        logger.info(f"Created and subscribed PubSub instance for user {user_id} on channel {channel}")
        return pubsub

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

    async def send_message(self, message: str, user_id: uuid.UUID, connection_id: str | None = None) -> None:
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
            except (WebSocketDisconnect, RuntimeError, ConnectionError, OSError) as e:
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

    def publish_notification(self, user_id: uuid.UUID, message: dict[str, Any]) -> None:
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
        except redis.RedisError as e:
            logger.error(f"Failed to publish notification to Redis: {e}")

    def publish_broadcast(self, message: dict[str, Any]) -> None:
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
        except redis.RedisError as e:
            logger.error(f"Failed to publish broadcast to Redis: {e}")

    async def listen_to_redis(self, user_id: uuid.UUID, websocket: WebSocket) -> None:
        """
        Listen to Redis Pub/Sub for a specific user and forward messages to WebSocket.

        This runs blocking Redis operations in a thread pool to avoid blocking
        the async event loop. Each user gets their own PubSub instance.

        Args:
            user_id: UUID of the user
            websocket: The WebSocket connection to send messages to
        """
        # Create a dedicated PubSub instance for this user
        pubsub = self._create_pubsub_for_user(user_id)
        channel = f"user:{user_id}"

        logger.info(f"Starting Redis listener for user {user_id} on channel {channel}")

        try:
            # Run the blocking pubsub.listen() in a thread pool
            loop = asyncio.get_event_loop()

            while True:
                # Get next message from Redis (non-blocking via thread pool)
                message = await loop.run_in_executor(
                    self._executor,
                    self._get_next_message,
                    pubsub
                )

                if message is None:
                    # Connection closed or timeout
                    break

                if message["type"] == "message":
                    data = message["data"]
                    try:
                        # Forward to WebSocket
                        await websocket.send_text(data)
                        logger.debug(f"Forwarded Redis message to user {user_id}: {data[:100]}...")
                    except (WebSocketDisconnect, RuntimeError, ConnectionError, OSError) as e:
                        logger.error(f"Failed to forward Redis message to WebSocket: {e}")
                        break

                elif message["type"] == "unsubscribe":
                    # Connection closed
                    logger.info(f"Received unsubscribe signal for user {user_id}")
                    break

                elif message["type"] == "punsubscribe":
                    # Pattern unsubscribe
                    logger.info(f"Received punsubscribe signal for user {user_id}")
                    break

        except (WebSocketDisconnect, RuntimeError, ConnectionError, OSError, redis.RedisError) as e:
            logger.error(f"Error in Redis listener for user {user_id}: {e}")
        finally:
            try:
                pubsub.unsubscribe(channel)
                pubsub.close()
                logger.info(f"Unsubscribed and closed PubSub for user {user_id}")
            except redis.RedisError as e:
                logger.error(f"Error cleaning up PubSub for user {user_id}: {e}")

    def _get_next_message(self, pubsub: redis.client.PubSub) -> dict[str, Any] | None:
        """
        Get the next message from PubSub (blocking, runs in thread pool).

        Args:
            pubsub: The PubSub instance to listen on

        Returns:
            Message dict or None if connection closed
        """
        try:
            for message in pubsub.listen():
                return message
        except redis.RedisError as e:
            logger.error(f"Error getting message from PubSub: {e}")
            return None

    def get_connection_count(self, user_id: uuid.UUID | None = None) -> int:
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


def emit_task_update(user_id: uuid.UUID, data: dict[str, Any]) -> None:
    """Send a task progress update with a UTC timestamp."""
    notify_user(
        user_id=user_id,
        notification_type="TASK_UPDATE",
        data={
            **data,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


def notify_user(user_id: uuid.UUID, notification_type: str, data: dict[str, Any]) -> None:
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


def broadcast_notification(notification_type: str, data: dict[str, Any]) -> None:
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
    'broadcast_notification',
    'emit_task_update',
    'manager',
    'notify_user'
]
