import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.schemas import Platform
from platform_registry.tests.utils import random_email, random_lower_string, setup_new_platform

USER_DATA = {"username": random_email().split("@")[0],
             "firstname": "User",
             "lastname": "USER",
             "email": random_email(),
             "password": random_lower_string(),
             }

@pytest.fixture(scope='class')
def sample_platform(db: Session) -> Platform:
    p = setup_new_platform(db=db, name="Sample Platform")
    yield p
    db.delete(p)
    db.commit()


class TestUsers:

    def test_platform_user_cannot_create_users(self,
                                               client: TestClient,
                                               platform_user_auth_headers) -> None:
        response = client.post(url="/users/",
                               json=USER_DATA,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_create_users(self,
                                    client: TestClient,
                                    admin_user_auth_headers) -> None:
        response = client.post(url="/users/",
                               json=USER_DATA,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert "id" in content
