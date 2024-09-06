from typing import List

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.models import User
from platform_registry.schemas import Platform
from platform_registry.services import access_keys
from platform_registry.tests.utils import setup_new_platform


@pytest.fixture(scope='class')
def sample_platforms(db: Session) -> List[Platform]:
    platforms = []
    n = 5
    for i in range(n):
        platforms.append(setup_new_platform(db=db, name=f"Platform_{i}"))
    yield platforms
    for p in platforms:
        key = access_keys.get_platform_current_valid_key(db=db, platform_id=p.id)
        db.delete(key)
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
        response = client.get(url="/platforms/recipients/", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success_listing_platforms_to_share_project_as_platform_user(self,
                                                                         client: TestClient,
                                                                         platform_user_auth_headers,
                                                                         sample_platforms: List[Platform]):
        # returns all other platforms
        response = client.get(url="/platforms/recipients/", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == len(sample_platforms)
        assert all(k in ('id', 'name') for k in content[0].keys()), "Response items have extra keys"


    def test_failure_creating_platform_as_platform_user(self,
                                                        client: TestClient,
                                                        platform_user_auth_headers: dict):
        platform_data = {"name": "some platform"}
        response = client.post(url="/platforms/",
                               json=platform_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
        assert content["user_account"] is not None
        assert len(content["access_keys"]) == 1


    def test_success_patch_platform_as_admin_user(self,
                                                  client: TestClient,
                                                  admin_user_auth_headers: dict,
                                                  sample_platform: Platform,
                                                  db: Session):
        initial_name = sample_platform.name
        patch_data = {"name": "New name for platform"}
        response = client.patch(url=f"/platforms/{sample_platform.id}",
                                json=patch_data,
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["name"] != initial_name
        db.refresh(sample_platform)
        assert sample_platform.name == patch_data["name"]



    def test_success_patch_platform_as_platform_user(self,
                                                     client: TestClient,
                                                     platform_user: User,
                                                     platform_user_auth_headers: dict,
                                                     db: Session):
        target_platform = platform_user.platform
        initial_name = target_platform.name
        patch_data = {"name": "New name for platform"}
        response = client.patch(url=f"/platforms/{target_platform.id}",
                                json=patch_data,
                                headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["name"] != initial_name
        db.refresh(target_platform)
        assert target_platform.name == patch_data["name"]


    def test_error_patch_not_owned_platform_as_platform_user(self,
                                                             client: TestClient,
                                                             platform_user: User,
                                                             platform_user_auth_headers: dict,
                                                             sample_platform: Platform):
        assert platform_user.platform_id != sample_platform.id
        patch_data = {"name": "New name for platform"}
        response = client.patch(url=f"/platforms/{sample_platform.id}",
                                json=patch_data,
                                headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        content = response.json()
