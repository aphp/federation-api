from datetime import datetime, timedelta
from typing import List

import pytest
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from platform_registry.services import access_keys
from platform_registry.models import User, AccessKey, Platform
from platform_registry.tests.utils import create_access_key, setup_new_platform


@pytest.fixture(scope='function')
def sample_keys(db: Session) -> List[AccessKey]:
    n = 5
    keys = []
    for i in range(n):
        platform = setup_new_platform(db=db, name=f"Platform_with_key_{i}")
        key = access_keys.get_platform_current_valid_key(db=db, platform_id=platform.id)
        keys.append(key)
    yield keys
    for k in keys:
        db.delete(k)
        db.delete(k.platform)
    db.commit()


@pytest.fixture(scope='function')
def sample_key(db: Session, platform_user: User) -> AccessKey:
    key = access_keys.get_platform_current_valid_key(db=db, platform_id=platform_user.platform_id)
    yield key


class TestAccessKeys:

    def test_list_platform_own_access_keys(self,
                                           client: TestClient,
                                           platform_user_auth_headers: dict,
                                           sample_key: AccessKey):
        response = client.get(url="/platforms/access-keys/my-keys", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == 1
        own_key = content[0]
        assert own_key["id"] == sample_key.id
        assert own_key["key"] == sample_key.key

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
                                                    db: Session,
                                                    sample_keys: List[AccessKey]):
        response = client.get(url="/platforms/access-keys/", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == len(sample_keys) + 1

    def test_success_get_access_key_by_id(self,
                                          client: TestClient,
                                          admin_user_auth_headers: dict,
                                          sample_key: AccessKey):
        response = client.get(url=f"/platforms/access-keys/{sample_key.id}", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["id"] == sample_key.id
        assert content["key"] == sample_key.key

    def test_success_create_access_key_as_admin_user(self,
                                                     client: TestClient,
                                                     admin_user_auth_headers: dict,
                                                     sample_platform: Platform,
                                                     db: Session):
        # delete existing key for platform
        key = access_keys.get_platform_current_valid_key(db=db, platform_id=sample_platform.id)
        db.delete(key)
        db.commit()

        key_data = {"platform_id": sample_platform.id
                    }
        response = client.post(url="/platforms/access-keys/",
                               json=key_data,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert "id" in content
        assert "key" in content
        assert "start_datetime" in content
        assert "end_datetime" in content
        key = access_keys.get_access_key_by_id(db=db, key_id=content["id"])
        assert key is not None

    def test_failure_create_access_keys_as_platform_user(self,
                                                         client: TestClient,
                                                         platform_user_auth_headers: dict,
                                                         sample_platform: Platform):
        key_data = {"platform_id": sample_platform.id
                    }
        response = client.post(url="/platforms/access-keys/",
                               json=key_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success_patch_access_key(self,
                                      client: TestClient,
                                      admin_user_auth_headers: dict,
                                      sample_key: AccessKey):
        initial_end_datetime = sample_key.end_datetime
        patch_data = {"start_datetime": None,
                      "end_datetime": datetime.strftime(datetime.now() + timedelta(days=7),
                                                        "%Y-%m-%d %H:%M:%S"),
                      }
        response = client.patch(url=f"/platforms/access-keys/{sample_key.id}/",
                                json=patch_data,
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["start_datetime"] == datetime.strftime(sample_key.start_datetime, "%m/%d/%Y, %H:%M:%S")
        assert content["end_datetime"] != datetime.strftime(initial_end_datetime, "%m/%d/%Y, %H:%M:%S")

    def test_error_patch_access_key_with_wrong_dates(self,
                                                     client: TestClient,
                                                     admin_user_auth_headers: dict,
                                                     sample_key: AccessKey):
        initial_start_datetime = sample_key.start_datetime
        initial_end_datetime = sample_key.end_datetime
        patch_data = {"start_datetime": datetime.strftime(initial_end_datetime, "%Y-%m-%d %H:%M:%S"),
                      "end_datetime": datetime.strftime(initial_start_datetime, "%Y-%m-%d %H:%M:%S"),
                      }
        response = client.patch(url=f"/platforms/access-keys/{sample_key.id}/",
                                json=patch_data,
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_success_archive_access_key(self,
                                        client: TestClient,
                                        admin_user_auth_headers: dict,
                                        db: Session,
                                        sample_key: AccessKey):
        response = client.patch(url=f"/platforms/access-keys/{sample_key.id}/archive/",
                                json={},
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert datetime.strptime(content["end_datetime"], "%m/%d/%Y, %H:%M:%S") <= datetime.now()
        db.refresh(sample_key)
        assert sample_key.deleted_at is not None
