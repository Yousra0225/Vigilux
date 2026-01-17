"""
Tests for notification settings API endpoints.

Covers:
- GET /api/v1/users/me/notifications - List notification settings
- POST /api/v1/users/me/notifications - Create notification setting
- PATCH /api/v1/users/me/notifications/{id} - Update notification setting
- DELETE /api/v1/users/me/notifications/{id} - Delete notification setting
"""

import pytest
from fastapi import status

from app.models.notification import NotificationChannel


class TestListNotificationSettings:
    """Tests for listing notification settings endpoint."""

    def test_list_settings_empty(self, test_client, auth_headers):
        """Should create default email settings when none exist."""
        response = test_client.get(
            "/api/v1/users/me/notifications",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["channel"] == "email"
        assert data[0]["enabled"] is True
        assert data[0]["min_score"] == 50

    def test_list_settings_with_data(self, test_client, auth_headers, notification_settings):
        """Should return all notification settings for user."""
        response = test_client.get(
            "/api/v1/users/me/notifications",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_settings_unauthenticated(self, test_client):
        """Should reject request without authentication."""
        response = test_client.get("/api/v1/users/me/notifications")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateNotificationSetting:
    """Tests for creating notification settings endpoint."""

    def test_create_setting_success(self, test_client, auth_headers):
        """Should create new notification setting."""
        response = test_client.post(
            "/api/v1/users/me/notifications",
            headers=auth_headers,
            json={
                "channel": "slack",
                "min_score": 70,
                "enabled": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["channel"] == "slack"
        assert data["min_score"] == 70
        assert data["enabled"] is True

    def test_create_setting_duplicate_channel(self, test_client, auth_headers):
        """Should reject duplicate channel for same user."""
        # Create first setting
        test_client.post(
            "/api/v1/users/me/notifications",
            headers=auth_headers,
            json={
                "channel": "slack",
                "min_score": 70,
                "enabled": True
            }
        )

        # Try to create duplicate
        response = test_client.post(
            "/api/v1/users/me/notifications",
            headers=auth_headers,
            json={
                "channel": "slack",
                "min_score": 80,
                "enabled": True
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exist" in response.json()["detail"].lower()

    def test_create_setting_whatsapp_growth(self, test_client, auth_headers):
        """Should allow creating WhatsApp setting for Growth user (no restriction at creation)."""
        response = test_client.post(
            "/api/v1/users/me/notifications",
            headers=auth_headers,
            json={
                "channel": "whatsapp",
                "min_score": 60,
                "enabled": True
            }
        )
        # Creation should succeed (restriction is enforced at dispatch time)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["channel"] == "whatsapp"

    def test_create_setting_unauthenticated(self, test_client):
        """Should reject request without authentication."""
        response = test_client.post(
            "/api/v1/users/me/notifications",
            json={
                "channel": "slack",
                "min_score": 70,
                "enabled": True
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateNotificationSetting:
    """Tests for updating notification settings endpoint."""

    def test_update_setting_success(self, test_client, auth_headers, notification_settings, db_session):
        """Should update notification setting."""
        setting = notification_settings[0]
        response = test_client.patch(
            f"/api/v1/users/me/notifications/{setting.id}",
            headers=auth_headers,
            json={"min_score": 80}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["min_score"] == 80

    def test_update_setting_multiple_fields(self, test_client, auth_headers, notification_settings):
        """Should update multiple fields at once."""
        setting = notification_settings[0]
        response = test_client.patch(
            f"/api/v1/users/me/notifications/{setting.id}",
            headers=auth_headers,
            json={
                "min_score": 90,
                "enabled": False
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["min_score"] == 90
        assert data["enabled"] is False

    def test_update_setting_not_found(self, test_client, auth_headers):
        """Should return 404 for non-existent setting."""
        import uuid
        fake_id = uuid.uuid4()
        response = test_client.patch(
            f"/api/v1/users/me/notifications/{fake_id}",
            headers=auth_headers,
            json={"min_score": 80}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_setting_unauthorized(self, test_client, auth_headers, auth_headers_starter, db_session, test_user_starter):
        """Should prevent updating another user's settings."""
        # Create setting for starter user
        from app.models.notification import NotificationSettings
        setting = NotificationSettings(
            user_id=test_user_starter.id,
            channel=NotificationChannel.EMAIL,
            min_score=50,
            enabled=True
        )
        db_session.add(setting)
        db_session.commit()

        # Try to update with different user's token
        response = test_client.patch(
            f"/api/v1/users/me/notifications/{setting.id}",
            headers=auth_headers,  # Using growth user's token
            json={"min_score": 80}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_setting_unauthenticated(self, test_client, notification_settings):
        """Should reject request without authentication."""
        setting = notification_settings[0]
        response = test_client.patch(
            f"/api/v1/users/me/notifications/{setting.id}",
            json={"min_score": 80}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteNotificationSetting:
    """Tests for deleting notification settings endpoint."""

    def test_delete_setting_success(self, test_client, auth_headers, notification_settings, db_session):
        """Should delete notification setting."""
        setting = notification_settings[0]
        response = test_client.delete(
            f"/api/v1/users/me/notifications/{setting.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"ok": True}

        # Verify deletion
        response = test_client.get(
            "/api/v1/users/me/notifications",
            headers=auth_headers
        )
        assert len(response.json()) == 2  # Started with 3, deleted 1

    def test_delete_setting_not_found(self, test_client, auth_headers):
        """Should return 404 for non-existent setting."""
        import uuid
        fake_id = uuid.uuid4()
        response = test_client.delete(
            f"/api/v1/users/me/notifications/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_setting_unauthorized(self, test_client, auth_headers, auth_headers_starter, db_session, test_user_starter):
        """Should prevent deleting another user's settings."""
        from app.models.notification import NotificationSettings
        setting = NotificationSettings(
            user_id=test_user_starter.id,
            channel=NotificationChannel.EMAIL,
            min_score=50,
            enabled=True
        )
        db_session.add(setting)
        db_session.commit()

        # Try to delete with different user's token
        response = test_client.delete(
            f"/api/v1/users/me/notifications/{setting.id}",
            headers=auth_headers  # Using growth user's token
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_setting_unauthenticated(self, test_client, notification_settings):
        """Should reject request without authentication."""
        setting = notification_settings[0]
        response = test_client.delete(f"/api/v1/users/me/notifications/{setting.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationSettingsIntegration:
    """Integration tests for notification settings."""

    def test_full_crud_flow(self, test_client, auth_headers, db_session):
        """Test complete CRUD flow for notification settings."""
        # 1. Create
        create_response = test_client.post(
            "/api/v1/users/me/notifications",
            headers=auth_headers,
            json={
                "channel": "slack",
                "min_score": 70,
                "enabled": True
            }
        )
        assert create_response.status_code == status.HTTP_200_OK
        created = create_response.json()
        setting_id = created["id"]

        # 2. Read
        list_response = test_client.get(
            "/api/v1/users/me/notifications",
            headers=auth_headers
        )
        settings = list_response.json()
        slack_setting = next((s for s in settings if s["channel"] == "slack"), None)
        assert slack_setting is not None
        assert slack_setting["id"] == setting_id

        # 3. Update
        update_response = test_client.patch(
            f"/api/v1/users/me/notifications/{setting_id}",
            headers=auth_headers,
            json={"min_score": 90}
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["min_score"] == 90

        # 4. Delete
        delete_response = test_client.delete(
            f"/api/v1/users/me/notifications/{setting_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_200_OK

        # Verify deletion
        list_response = test_client.get(
            "/api/v1/users/me/notifications",
            headers=auth_headers
        )
        settings = list_response.json()
        slack_setting = next((s for s in settings if s["channel"] == "slack"), None)
        assert slack_setting is None
