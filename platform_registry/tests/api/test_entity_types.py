import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.tests.utils import create_random_entity_type, retrieve_all_entity_types


class TestEntityTypes:

    def test_admin_can_fetch_entity_types(self,
                                          client: TestClient,
                                          admin_user_authorization_headers: dict[str, str],
                                          db: Session) -> None:
        n = 5
        types = retrieve_all_entity_types(db=db)

        if types:
            n = len(types)
        else:
            for i in range(n):
                create_random_entity_type(db=db, name=f"EntityType_{i}")

        response = client.get(url="/entities/types/", headers=admin_user_authorization_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == n

    def test_platform_user_cannot_fetch_entity_types(self,
                                                     client: TestClient,
                                                     platform_user_authorization_headers: dict[str, str]) -> None:
        response = client.get(url="/entities/types/", headers=platform_user_authorization_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_create_entity_type(self,
                                          client: TestClient,
                                          admin_user_authorization_headers: dict[str, str]) -> None:
        response = client.post(url="/entities/types/",
                               json={"name": "Special Entity Type"},
                               headers=admin_user_authorization_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_platform_user_cannot_create_entity_type(self,
                                                     client: TestClient,
                                                     platform_user_authorization_headers: dict[str, str]) -> None:
        response = client.post(url="/entities/types/",
                               json={"name": "Special Entity Type"},
                               headers=platform_user_authorization_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
