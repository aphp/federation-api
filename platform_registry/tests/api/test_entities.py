import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.schemas import EntityType
from platform_registry.tests.utils import create_random_entity, create_random_entity_type


@pytest.fixture(scope='function')
def sample_entity_type(db: Session) -> EntityType:
    return create_random_entity_type(name="some entity type", db=db)


class TestEntities:

    def test_admin_and_platforms_can_fetch_entities(self,
                                                    client: TestClient,
                                                    admin_user_auth_headers,
                                                    platform_user_auth_headers,
                                                    db: Session) -> None:
        n = 5
        for i in range(n):
            create_random_entity(db=db, name=f"Entity_{i}")

        for user_headers in (admin_user_auth_headers,
                             platform_user_auth_headers):
            response = client.get(url="/entities/", headers=user_headers)
            assert response.status_code == status.HTTP_200_OK
            content = response.json()
            assert len(content) == n

    def test_admin_can_create_entity(self,
                                     client: TestClient,
                                     admin_user_auth_headers,
                                     sample_entity_type: EntityType) -> None:
        entity_data = {"name": "Special Entity",
                       "entity_type_id": sample_entity_type.id
                       }
        response = client.post(url="/entities/",
                               json=entity_data,
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_platform_user_cannot_create_entity(self,
                                                client: TestClient,
                                                platform_user_auth_headers,
                                                sample_entity_type: EntityType) -> None:
        entity_data = {"name": "Special Entity",
                       "entity_type_id": sample_entity_type.id
                       }
        response = client.post(url="/entities/",
                               json=entity_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
