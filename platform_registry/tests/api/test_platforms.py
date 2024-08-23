from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.models import User
from platform_registry.tests.utils import create_platform, create_access_key


@pytest.fixture(scope='class')
def sample_platforms(db: Session) -> int:
    n = 5
    for i in range(n):
        create_platform(db=db, name=f"Platform_{i}")
    return n


class TestPlatforms:

    def test_list_platforms_as_admin_user(self,
                                          client: TestClient,
                                          admin_user_auth_headers: dict,
                                          sample_platforms: int):
        response = client.get(url="/platforms/", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == sample_platforms + 1

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
                                                                         sample_platforms: int):
        # returns all other platforms
        response = client.get(url="/platforms/project-share/", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == sample_platforms


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


class TestAccessKeys:

    def test_list_platform_own_access_keys(self,
                                           client: TestClient,
                                           platform_user: User,
                                           platform_user_auth_headers: dict,
                                           db: Session):
        key = create_access_key(db=db, platform_id=platform_user.platform_id)
        response = client.get(url="/platforms/access-keys/my-keys", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        own_key = content[0]
        assert own_key["id"] == key.id
        assert own_key["key"] == key.key

    def test_failure_list_platform_own_access_keys_as_admin_user(self,
                                                                 client: TestClient,
                                                                 admin_user_auth_headers: dict):
        # only platform-users allowed to call this endpoint
        response = client.get(url="/platforms/access-keys/my-keys", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_failure_list_access_keys_as_platform_user(self,
                                                       client: TestClient,
                                                       platform_user_auth_headers: dict):
        response = client.get(url="/platforms/access-keys", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success_list_access_keys_as_admin_user(self,
                                                    client: TestClient,
                                                    admin_user_auth_headers: dict,
                                                    db: Session):
        n = 5
        for i in range(n):
            platform = create_platform(db=db, name=f"Platform_with_key_{i}")
            create_access_key(db=db, platform_id=platform.id)

        response = client.get(url="/platforms/access-keys/", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == n + 1

    def test_success_get_access_key_by_id(self,
                                          client: TestClient,
                                          platform_user: User,
                                          admin_user_auth_headers: dict):
        key = platform_user.platform.access_keys[0]
        response = client.get(url=f"/platforms/access-keys/{key.id}", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["id"] == key.id
        assert content["key"] == key.key

    def test_success_create_access_key_as_admin_user(self,
                                                     client: TestClient,
                                                     admin_user_auth_headers: dict,
                                                     db: Session):
        new_platform = create_platform(db=db, name=f"new platform to create access key")
        key_data = {"platform_id": new_platform.id
                    }
        response = client.post(url="/platforms/access-keys/",
                               json=key_data,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert content["name"][:8] == key_data["platform_id"][:8]
        assert "id" in content
        assert "key" in content
        assert "start_datetime" in content
        assert "end_datetime" in content

    def test_failure_create_access_keys_as_platform_user(self,
                                                         client: TestClient,
                                                         platform_user_auth_headers: dict,
                                                         db: Session):
        new_platform = create_platform(db=db, name=f"new platform to create access key 2")
        key_data = {"platform_id": new_platform.id
                    }
        response = client.post(url="/platforms/access-keys/",
                               json=key_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success_patch_access_key(self,
                                      client: TestClient,
                                      platform_user,
                                      admin_user_auth_headers: dict):
        existing_key = platform_user.platform.access_keys[0]
        initial_end_datetime = existing_key.end_datetime
        patch_data = {"start_datetime": None,
                      "end_datetime": datetime.strftime(datetime.now() + timedelta(days=7),
                                                        "%Y-%m-%d %H:%M:%S"),
                      }
        response = client.patch(url=f"/platforms/access-keys/{existing_key.id}/",
                                json=patch_data,
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["start_datetime"] == datetime.strftime(existing_key.start_datetime, "%m/%d/%Y, %H:%M:%S")
        assert content["end_datetime"] != datetime.strftime(initial_end_datetime, "%m/%d/%Y, %H:%M:%S")

    def test_error_patch_access_key_with_wrong_dates(self,
                                                     client: TestClient,
                                                     platform_user,
                                                     admin_user_auth_headers: dict):
        existing_key = platform_user.platform.access_keys[0]
        initial_start_datetime = existing_key.start_datetime
        initial_end_datetime = existing_key.end_datetime
        patch_data = {"start_datetime": datetime.strftime(initial_end_datetime, "%Y-%m-%d %H:%M:%S"),
                      "end_datetime": datetime.strftime(initial_start_datetime, "%Y-%m-%d %H:%M:%S"),
                      }
        response = client.patch(url=f"/platforms/access-keys/{existing_key.id}/",
                                json=patch_data,
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_success_archive_access_key(self,
                                        client: TestClient,
                                        platform_user,
                                        admin_user_auth_headers: dict,
                                        db: Session):
        existing_key = platform_user.platform.access_keys[0]
        response = client.patch(url=f"/platforms/access-keys/{existing_key.id}/archive/",
                                json={},
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert datetime.strptime(content["end_datetime"], "%m/%d/%Y, %H:%M:%S") <= datetime.now()
        db.refresh(existing_key)
        assert existing_key.deleted_at is not None

