import random
import string
from datetime import date, timedelta
from typing import Tuple, List

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from platform_registry.services import users, roles, entities, platforms, access_keys, projects
from platform_registry import schemas
from platform_registry.services.users import ADMIN_PASSWORD


def random_lower_string(l: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=l))


def random_email() -> str:
    return f"{random_lower_string()}@platform-registry.fr"



def get_or_create_admin_role(db: Session) -> schemas.Role:
    admin_role = roles.get_admin_role(db=db)
    if admin_role:
        return admin_role
    role_in = schemas.RoleCreate(name="Registry Admin",
                                 is_registry_admin=True,
                                 is_platform=False)
    return roles.create_role(db, role_in)


def get_or_create_platform_role(db: Session) -> schemas.Role:
    platform_role = roles.get_platform_role(db=db)
    if platform_role:
        return platform_role
    role_in = schemas.RoleCreate(name="Platform Role",
                                 is_registry_admin=False,
                                 is_platform=True)
    return roles.create_role(db, role_in)


def setup_new_platform(db: Session, name: str) -> schemas.Platform:
    return platforms.setup_platform(db=db, platform=schemas.PlatformCreate(name=name))


def create_admin_user(db: Session) -> Tuple[schemas.RegularUser, str]:
    admin_role = get_or_create_admin_role(db)
    user = users.create_admin_user(db=db, role=admin_role)
    return user, ADMIN_PASSWORD


def create_platform_user(db: Session) ->  Tuple[schemas.PlatformUser, str]:
    _ = get_or_create_platform_role(db=db)
    platform = setup_new_platform(db=db, name="Platform")
    password = access_keys.get_platform_current_valid_key(db=db, platform_id=platform.id).key
    return platform.user_account[0], password


def get_main_platform_user(db: Session) -> schemas.SystemUser:
    return users.get_user_by_username(db=db, username="platform")


def retrieve_all_entity_types(db: Session) -> List[schemas.EntityType]:
    return entities.get_entity_types(db=db)


def create_random_entity_type(name: str, db: Session) -> schemas.EntityType:
    type_in = schemas.EntityTypeCreate(name=name)
    return entities.create_entity_type(db=db, entity_type=type_in)


def create_random_entity(name: str, db: Session) -> None:
    entity_type_name = f"type_{name}"
    entity_type = create_random_entity_type(name=entity_type_name, db=db)
    entity_in = schemas.EntityCreate(name=name, entity_type_id=entity_type.id)
    entities.create_entity(db=db, entity=entity_in)


def get_authorization_headers(client: TestClient, db: Session, for_admin: bool = False) -> dict[str, str]:
    if for_admin:
        user, password = create_admin_user(db)
    else:
        user, password = create_platform_user(db)

    login_data = {"username": user.username,
                  "password": password,
                  }
    response = client.post(url="/auth/login",
                           data=login_data,
                           headers={'Content-Type': "application/x-www-form-urlencoded"})
    login_response = response.json()
    token = login_response["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers

def create_access_key(db: Session, platform_id: str):
    key = schemas.AccessKeyCreate(platform_id=platform_id)
    return access_keys.create_access_key(db=db, access_key=key)


def create_project(db: Session, platform_id: str) -> schemas.Project:
    project_in = schemas.ProjectCreate(name=random_lower_string(l=10),
                               code=random_lower_string(l=5),
                               description="some project description",
                               start_date=date.today(),
                               end_date=date.today() + timedelta(days=30),
                               framework_ids=[])
    return projects.create_project(db, project_in, platform_id)
