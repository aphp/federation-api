import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.schemas import Platform
from platform_registry.tests.utils import random_email, random_lower_string, create_platform

USER_DATA = {"username": random_email().split("@")[0],
             "firstname": "User",
             "lastname": "USER",
             "email": random_email(),
             "password": random_lower_string(),
             }

@pytest.fixture(scope='class')
def sample_platform(db: Session) -> Platform:
    return create_platform(db=db, name="Sample Platform")


class TestUsers:

    def test_platform_user_cannot_create_users(self,
                                               client: TestClient,
                                               platform_user_auth_headers) -> None:
        response = client.post(url="/users/",
                               json=USER_DATA,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_create_regular_user(self,
                                           client: TestClient,
                                           admin_user_auth_headers) -> None:
        response = client.post(url="/users/",
                               json=USER_DATA,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert "id" in content

    def test_admin_can_create_platform_user(self,
                                            client: TestClient,
                                            admin_user_auth_headers,
                                            platform_role,
                                            sample_platform) -> None:
        platform_user_data = {**USER_DATA,
                              "username": random_email().split("@")[0],
                              "email": random_email(),
                              "role_id": platform_role.id,
                              "platform_id": sample_platform.id
                              }
        response = client.post(url="/users/",
                               json=platform_user_data,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert "id" in content
        assert content["role"]["id"] == platform_role.id
        assert content["role"]["is_platform"] == True

    def test_failure_create_platform_user_without_platform_role(self,
                                                                client: TestClient,
                                                                admin_user_auth_headers,
                                                                sample_platform) -> None:
        platform_user_data = {**USER_DATA,
                              "username": random_email().split("@")[0],
                              "email": random_email(),
                              "platform_id": sample_platform.id
                              }
        response = client.post(url="/users/",
                               json=platform_user_data,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST




