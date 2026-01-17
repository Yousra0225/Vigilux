"""
Tests for projects API endpoints.

Covers:
- GET /api/v1/projects/ - List user's projects
"""

import pytest
from fastapi import status

from app.models.project import Project
from app.core.security import get_password_hash
from app.models.user import User


class TestListProjects:
    """Tests for listing projects endpoint."""

    def test_list_projects_empty(self, test_client, auth_headers):
        """Should return empty list when user has no projects."""
        response = test_client.get(
            "/api/v1/projects/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_projects_with_data(self, test_client, auth_headers, test_project):
        """Should return list of user's projects."""
        response = test_client.get(
            "/api/v1/projects/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(test_project.id)
        assert data[0]["url"] == test_project.url
        assert data[0]["description"] == test_project.description

    def test_list_projects_multiple(self, test_client, auth_headers, db_session, test_user):
        """Should return all user's projects."""
        # Create multiple projects
        for i in range(3):
            project = Project(
                user_id=test_user.id,
                url=f"https://project{i}.com",
                description=f"Project {i}"
            )
            db_session.add(project)
        db_session.commit()

        response = test_client.get(
            "/api/v1/projects/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_projects_only_own(self, test_client, auth_headers, db_session, test_user):
        """Should only return user's own projects, not others."""
        # Create another user with project
        other_user = User(
            email="other@example.com",
            hashed_password=get_password_hash("password"),
            plan_type="starter"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        other_project = Project(
            user_id=other_user.id,
            url="https://other.com",
            description="Other's project"
        )
        db_session.add(other_project)
        db_session.commit()

        # Create user's project
        user_project = Project(
            user_id=test_user.id,
            url="https://mine.com",
            description="My project"
        )
        db_session.add(user_project)
        db_session.commit()

        response = test_client.get(
            "/api/v1/projects/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["url"] == "https://mine.com"

    def test_list_projects_unauthenticated(self, test_client):
        """Should reject request without authentication."""
        response = test_client.get("/api/v1/projects/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_projects_invalid_token(self, test_client):
        """Should reject request with invalid token."""
        response = test_client.get(
            "/api/v1/projects/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
