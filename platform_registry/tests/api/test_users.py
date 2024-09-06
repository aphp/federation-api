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


class TestUsers:

    def test_admin_can_create_regular_users(self,
                                            client: TestClient,
                                            admin_user_auth_headers) -> None:
        response = client.post(url="/users/regular/",
                               json=USER_DATA,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert "id" in content

    def test_platform_user_can_create_regular_users(self,
                                                    client: TestClient,
                                                    platform_user_auth_headers) -> None:
        user_data = {**USER_DATA,
                     "username": random_email().split("@")[0],
                     "email": random_email()
                     }
        response = client.post(url="/users/regular/",
                               json=user_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert "id" in content

    # def test_admin_can_list_system_users(self,
    #                                      client: TestClient,
    #                                      admin_user_auth_headers) -> None:
    #     response = client.get(url="/users/system/", headers=admin_user_auth_headers)
    #     assert response.status_code == status.HTTP_200_OK
    #     content = response.json()
    #     assert len(content) != 0
