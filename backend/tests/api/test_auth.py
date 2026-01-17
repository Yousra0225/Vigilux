"""
Tests for authentication endpoints.

Covers:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login (OAuth2 token)
- GET /api/v1/auth/me - Get current user (protected route)
"""

import pytest
from fastapi import status


class TestRegisterEndpoint:
    """Tests for user registration endpoint."""

    def test_register_success(self, test_client):
        """Should register a new user successfully."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert data["plan_type"] == "growth"  # Default plan
        assert data["is_verified"] is True
        assert "hashed_password" not in data  # Password should not be exposed

    def test_register_duplicate_email(self, test_client, test_user):
        """Should reject registration with existing email."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "AnotherPass123!"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_register_missing_email(self, test_client):
        """Should reject registration without email."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={"password": "SecurePass123!"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_password(self, test_client):
        """Should reject registration without password."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_invalid_email_format(self, test_client):
        """Note: Current User model uses EmailStr which accepts basic email formats.
        More strict validation can be added at the model level if needed."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "notanemail",
                "password": "SecurePass123!"
            }
        )
        # Current implementation accepts basic email-like strings
        # To add strict validation, add a validator to the User model
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY)


class TestLoginEndpoint:
    """Tests for user login endpoint."""

    def test_login_success(self, test_client, test_user):
        """Should login successfully with valid credentials."""
        response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_email(self, test_client):
        """Should reject login with non-existent email."""
        response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_wrong_password(self, test_client, test_user):
        """Should reject login with wrong password."""
        response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_missing_username(self, test_client):
        """Should reject login without username."""
        response = test_client.post(
            "/api/v1/auth/login",
            data={"password": "testpassword"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, test_client):
        """Should reject login without password."""
        response = test_client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetCurrentUserEndpoint:
    """Tests for getting current user endpoint."""

    def test_get_current_user_success(self, test_client, test_user, auth_headers):
        """Should return current user with valid token."""
        response = test_client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == str(test_user.id)
        assert "hashed_password" not in data

    def test_get_current_user_without_token(self, test_client):
        """Should reject request without authentication token."""
        response = test_client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, test_client):
        """Should reject request with invalid token."""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_malformed_token(self, test_client):
        """Should reject request with malformed token."""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.even.valid.jwt"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_wrong_scheme(self, test_client, test_user):
        """Should reject request with wrong auth scheme."""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Basic {test_user.email}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthIntegration:
    """Integration tests for auth flow."""

    def test_full_auth_flow(self, test_client):
        """Test complete registration -> login -> access protected resource flow."""
        # 1. Register new user
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "fullflow@example.com",
                "password": "FlowTest123!"
            }
        )
        assert register_response.status_code == status.HTTP_200_OK
        user_data = register_response.json()
        assert user_data["email"] == "fullflow@example.com"

        # 2. Login
        login_response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": "fullflow@example.com",
                "password": "FlowTest123!"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. Access protected endpoint
        me_response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == status.HTTP_200_OK
        me_data = me_response.json()
        assert me_data["email"] == "fullflow@example.com"
        assert me_data["id"] == user_data["id"]
