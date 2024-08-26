from typing import List

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.models import User
from platform_registry.schemas import Platform
from platform_registry.tests.utils import create_platform


@pytest.fixture(scope='class')
def sample_platforms(db: Session) -> List[Platform]:
    platforms = []
    n = 5
    for i in range(n):
        platforms.append(create_platform(db=db, name=f"Platform_{i}"))
    yield platforms
    for p in platforms:
        db.delete(p)
    db.commit()


class TestPlatforms:

    def test_list_platforms_as_admin_user(self,
                                          client: TestClient,
                                          admin_user_auth_headers: dict,
                                          sample_platforms: List[Platform]):
        response = client.get(url="/platforms/", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == len(sample_platforms) + 1

    def test_list_platforms_as_platform_user(self,
                                             client: TestClient,
                                             platform_user: User,
                                             platform_user_auth_headers,
                                             db: Session):
        # returns only the platform linked to user
        response = client.get(url="/platforms/", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        assert content[0]['id'] == platform_user.platform.id
        assert content[0]['name'] == platform_user.platform.name


    def test_failure_listing_platforms_to_share_project_as_admin_user(self,
                                                                      client: TestClient,
                                                                      admin_user_auth_headers: dict):
        # only platform-users allowed to call this endpoint
        response = client.get(url="/platforms/project-share/", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success_listing_platforms_to_share_project_as_platform_user(self,
                                                                         client: TestClient,
                                                                         platform_user_auth_headers,
                                                                         sample_platforms: List[Platform]):
        # returns all other platforms
        response = client.get(url="/platforms/project-share/", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == len(sample_platforms)


    def test_success_create_platform_as_admin_user(self,
                                                   client: TestClient,
                                                   admin_user_auth_headers: dict):
        platform_data = {"name": "New platform created by registry admin"}
        response = client.post(url="/platforms/",
                               json=platform_data,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert "id" in content

    def test_failure_creating_platform_as_platform_user(self,
                                                        client: TestClient,
                                                        platform_user_auth_headers: dict):
        platform_data = {"name": "some platform"}
        response = client.post(url="/platforms/",
                               json=platform_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
