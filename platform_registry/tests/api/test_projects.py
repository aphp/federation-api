from typing import List

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.services import regulatory_frameworks, access_keys
from platform_registry.models import User, Project, PlatformsSharedProjectsRel, Platform
from platform_registry.schemas import RegulatoryFramework, RegulatoryFrameworkCreate, RegularUser, Entity
from platform_registry.tests.utils import create_project, setup_new_platform, random_lower_string, create_random_entity, create_regular_user


@pytest.fixture(scope='class')
def sample_reg_frameworks(db: Session) -> List[RegulatoryFramework]:
    frameworks = []
    for i in range(5):
        framework = regulatory_frameworks.create_regulatory_framework(db,
                                                                      RegulatoryFrameworkCreate(name=f"RegFramework {i}",
                                                                                                description_url=f"www.regframework{i}.com"))
        frameworks.append(framework)

    yield frameworks
    for f in frameworks:
        db.delete(f)
    db.commit()


@pytest.fixture(scope='class')
def sample_users(db: Session) -> List[Entity]:
    users = []
    for i in range(5):
        users.append(create_regular_user(db=db))
    yield users
    for u in users:
        db.delete(u)
    db.commit()


@pytest.fixture(scope='class')
def sample_entities(db: Session) -> List[Entity]:
    entities = []
    for i in range(5):
        entities.append(create_random_entity(db=db, name=random_lower_string(l=10)))
    yield entities
    for e in entities:
        db.delete(e)
    db.commit()


@pytest.fixture(scope='class')
def sample_projects(db: Session, platform_user: User,
                    sample_reg_frameworks: List[RegulatoryFramework],
                    sample_users: List[RegularUser],
                    sample_entities: List[Entity]) -> List[Project]:
    projects = []
    n = 5
    for i in range(n):
        projects.append(create_project(db=db,
                                       platform_id=platform_user.platform_id,
                                       framework_ids=[sample_reg_frameworks[0].id],
                                       user_ids=[sample_users[0].id, sample_users[1].id],
                                       entity_ids=[sample_entities[0].id, sample_entities[1].id]
                                       ))
    yield projects
    for p in projects:
        db.delete(p)
    db.commit()


@pytest.fixture(scope='function')
def shared_project(db: Session, platform_user: User) -> Project:
    new_platform = setup_new_platform(db=db, name=random_lower_string(l=10))
    project = create_project(db=db, platform_id=new_platform.id)
    project_share = PlatformsSharedProjectsRel(platform_id=platform_user.platform_id,
                                               project_id=project.id)
    db.add(project_share)
    db.commit()
    db.refresh(project_share)
    yield project
    db.delete(project_share)
    db.delete(project)
    key = access_keys.get_platform_current_valid_key(db=db, platform_id=new_platform.id)
    db.delete(key)
    db.delete(new_platform)
    db.commit()


class TestProjects:

    def test_list_projects_as_admin_user(self,
                                         client: TestClient,
                                         admin_user_auth_headers: dict,
                                         sample_projects: List[Project]):
        response = client.get(url="/projects/", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == len(sample_projects)

    def test_list_projects_as_platform_user(self,
                                            client: TestClient,
                                            platform_user_auth_headers: dict,
                                            platform_user: User,
                                            sample_projects: List[Project]):
        response = client.get(url="/projects/", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert len(content) == len(sample_projects)
        assert all(e["owner_platform"] == platform_user.platform.name for e in content)


    def test_retrieve_project_as_admin_user(self,
                                            client: TestClient,
                                            admin_user_auth_headers: dict,
                                            sample_projects: List[Project]):
        target_project = sample_projects[0]
        response = client.get(url=f"/projects/{target_project.id}", headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["id"] == target_project.id

    def test_retrieve_owned_project(self,
                                    client: TestClient,
                                    platform_user_auth_headers: dict,
                                    platform_user: User,
                                    sample_projects: List[Project]):
        target_project = sample_projects[0]
        response = client.get(url=f"/projects/{target_project.id}", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["id"] == target_project.id
        assert content["owner_platform"] == platform_user.platform.name

    def test_retrieve_project_shared_with_me(self,
                                             client: TestClient,
                                             platform_user_auth_headers: dict,
                                             platform_user: User,
                                             shared_project: Project):
        response = client.get(url=f"/projects/{shared_project.id}", headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["id"] == shared_project.id
        assert content["owner_platform"] != platform_user.platform.name
        assert shared_project in platform_user.platform.shared_projects

    def test_error_create_project_as_admin_user(self,
                                                client: TestClient,
                                                admin_user_auth_headers: dict):
        response = client.post(url="/projects/",
                               json={},
                               headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success_create_project_as_platform_user(self,
                                                     client: TestClient,
                                                     platform_user_auth_headers: dict,
                                                     platform_user: User,
                                                     sample_reg_frameworks: List[RegulatoryFramework],
                                                     sample_users: List[RegularUser],
                                                     sample_entities: List[Entity],
                                                     ):
        project_data = {"name": random_lower_string(l=10),
                        "code": random_lower_string(l=5),
                        "framework_ids": [sample_reg_frameworks[0].id],
                        "user_ids": [sample_users[0].id, sample_users[1].id],
                        "entity_ids": [sample_entities[0].id],
                        }
        response = client.post(url="/projects/",
                               json=project_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        content = response.json()
        assert content["owner_platform"] == platform_user.platform.name
        assert "start_date" in content
        assert "end_date" in content

    def test_error_patch_project_as_admin_user(self,
                                               client: TestClient,
                                               admin_user_auth_headers: dict,
                                               sample_projects: List[Project]):
        response = client.patch(url=f"/projects/{sample_projects[0].id}",
                                json={},
                                headers=admin_user_auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_patch_project_not_owned(self,
                                           client: TestClient,
                                           platform_user_auth_headers: dict,
                                           sample_projects: List[Project],
                                           sample_platform: Platform,
                                           db: Session):
        target_project = sample_projects[-1]
        target_project.owner_platform_id = sample_platform.id
        db.commit()
        response = client.patch(url=f"/projects/{target_project.id}",
                                json={},
                                headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success_patch_project_as_owner_platform(self,
                                                     client: TestClient,
                                                     platform_user_auth_headers: dict,
                                                     sample_projects: List[Project],
                                                     sample_reg_frameworks: List[RegulatoryFramework],
                                                     sample_users: List[RegularUser],
                                                     sample_entities: List[Entity],
                                                     db: Session):
        target_project = sample_projects[0]
        initial_name = target_project.name
        initial_code = target_project.code
        initial_frameworks = [f.name for f in target_project.regulatory_frameworks]
        initial_users = [u.username for u in target_project.involved_users]
        initial_entities = [e.name for e in target_project.involved_entities]

        patch_data = {"name": f"{target_project.name}__updated",
                      "code": f"{target_project.code}__updated",
                      "framework_ids": [sample_reg_frameworks[-1].id, sample_reg_frameworks[-2].id],
                      "user_ids": [sample_users[-1].id, sample_users[-2].id],
                      "entity_ids": [sample_entities[-1].id, sample_entities[-2].id],
                      }
        response = client.patch(url=f"/projects/{target_project.id}",
                                json=patch_data,
                                headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["name"] != initial_name
        assert content["code"] != initial_code
        resp_frameworks = [f["name"] for f in content["regulatory_frameworks"]]
        assert len(resp_frameworks) == 2
        assert all(f not in initial_frameworks for f in resp_frameworks)

        resp_users = [f["username"] for f in content["involved_users"]]
        assert len(resp_users) == 2
        assert all(f not in initial_users for f in resp_users)

        resp_entities = [f["name"] for f in content["involved_entities"]]
        assert len(resp_entities) == 2
        assert all(f not in initial_entities for f in resp_entities)

    def test_error_share_project_not_owned(self,
                                           client: TestClient,
                                           platform_user_auth_headers: dict,
                                           sample_projects: List[Project],
                                           sample_platform: Platform,
                                           db: Session):
        target_project = sample_projects[1]
        target_project.owner_platform_id = sample_platform.id
        db.commit()
        response = client.post(url=f"/projects/{target_project.id}/share/",
                               json={"recipient_platform_ids": []},
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success_share_project_as_owner_platform(self,
                                                     client: TestClient,
                                                     platform_user_auth_headers: dict,
                                                     sample_projects: List[Project],
                                                     sample_platform: Platform,
                                                     db: Session):
        recipient_platform = sample_platform
        target_project = sample_projects[2]
        assert target_project.owner_platform_id != recipient_platform.id
        initial_allowed_platforms = target_project.allowed_platforms

        share_data = {"recipient_platform_ids": [{"platform_id": recipient_platform.id,
                                                  "readonly": True
                                                  }]
                      }
        response = client.post(url=f"/projects/{target_project.id}/share/",
                               json=share_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["success"] == True
        db.refresh(target_project)
        assert target_project.allowed_platforms != initial_allowed_platforms
        assert recipient_platform in target_project.allowed_platforms

