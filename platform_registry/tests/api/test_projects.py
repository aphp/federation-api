from typing import List

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from platform_registry.crud import users, regulatory_frameworks
from platform_registry.models import User, Project, PlatformsSharedProjectsRel, ProjectsRegulatoryFrameworksRel, Platform
from platform_registry.schemas import UserCreate, RegulatoryFramework, RegulatoryFrameworkCreate
from platform_registry.tests.utils import create_project, create_platform, random_lower_string, random_email, get_or_create_platform_role


@pytest.fixture(scope='class')
def sample_projects(db: Session, platform_user: User) -> List[Project]:
    projects = []
    n = 5
    for i in range(n):
        projects.append(create_project(db=db, user=platform_user))
    yield projects
    for p in projects:
        db.delete(p)
    db.commit()


@pytest.fixture(scope='function')
def shared_project(db: Session, platform_user: User) -> Project:
    new_platform = create_platform(db=db, name=random_lower_string(l=10))
    user_in = UserCreate(username=random_lower_string(l=5),
                         firstname="Source",
                         lastname="PLATFORM",
                         email=random_email(),
                         password=random_lower_string(),
                         role_id=get_or_create_platform_role(db=db).id,
                         platform_id=new_platform.id)
    source_platform_user = users.create_user(db=db, user=user_in)
    project = create_project(db=db, user=source_platform_user)
    project_share = PlatformsSharedProjectsRel(platform_id=platform_user.platform_id,
                                               project_id=project.id)
    db.add(project_share)
    db.commit()
    db.refresh(project_share)
    yield project
    db.delete(project_share)
    db.delete(project)
    db.delete(source_platform_user)
    db.delete(new_platform)
    db.commit()


@pytest.fixture(scope='function')
def sample_reg_frameworks(db: Session) -> List[RegulatoryFramework]:
    frameworks = []
    framework_01 = RegulatoryFrameworkCreate(name="RegFramework 01", description_url="www.regframework01.com")
    framework_02 = RegulatoryFrameworkCreate(name="RegFramework 02", description_url="www.regframework02.com")
    for f in (framework_01, framework_02):
        framework = regulatory_frameworks.create_regulatory_framework(db, f)
        frameworks.append(framework)

    yield frameworks
    for f in frameworks:
        db.delete(f)
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
                                                     platform_user: User):
        project_data = {"name": random_lower_string(l=10),
                        "code": random_lower_string(l=5),
                        "framework_ids": []
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
                                                     db: Session):
        target_project = sample_projects[0]
        proj_frm = ProjectsRegulatoryFrameworksRel(project_id=target_project.id,
                                                   regulatory_framework_id=sample_reg_frameworks[0].id)
        db.add(proj_frm)
        db.commit()

        assert len(target_project.regulatory_frameworks) == 1

        initial_name = target_project.name
        initial_code = target_project.code
        initial_frameworks = [f.name for f in target_project.regulatory_frameworks]   # framework_01

        patch_data = {"name": f"{target_project.name}__updated",
                      "code": f"{target_project.code}__updated",
                      "framework_ids": [sample_reg_frameworks[1].id],   # framework_02
                      }
        response = client.patch(url=f"/projects/{target_project.id}",
                                json=patch_data,
                                headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content["name"] != initial_name
        assert content["code"] != initial_code
        assert content["regulatory_frameworks"] != initial_frameworks
        assert len(content["regulatory_frameworks"]) == 1

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
                                                     sample_platform: Platform):
        target_project = sample_projects[2]
        initial_allowed_platforms = target_project.allowed_platforms

        share_data = {"recipient_platform_ids": [{"platform_id": sample_platform.id,
                                                  "write": True
                                                  }]
                      }
        response = client.post(url=f"/projects/{target_project.id}/share/",
                               json=share_data,
                               headers=platform_user_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert target_project.allowed_platforms == initial_allowed_platforms

