import random
import string
from typing import Tuple, List

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from platform_registry.crud import users, roles, entities, platforms, access_keys
from platform_registry.schemas import EntityType, User, UserCreate, Role, RoleCreate, EntityTypeCreate, PlatformCreate, Entity, EntityCreate, \
    Platform, AccessKey, AccessKeyCreate


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@platform-registry.fr"



def get_or_create_admin_role(db: Session) -> Role:
    admin_role = roles.get_main_platform_role(db=db)
    if admin_role:
        return admin_role
    role_in = RoleCreate(name="Registry Admin",
                         is_registry_admin=True,
                         is_platform=False)
    return roles.create_role(db, role_in)


def get_or_create_platform_role(db: Session) -> Role:
    platform_role = roles.get_main_platform_role(db=db)
    if platform_role:
        return platform_role
    role_in = RoleCreate(name="Platform Role",
                         is_registry_admin=False,
                         is_platform=True)
    return roles.create_role(db, role_in)


def create_platform(db: Session, name: str) -> Platform:
    platform_in = PlatformCreate(name=name)
    return platforms.create_platform(db, platform_in)


def create_admin_user(db: Session) -> Tuple[User, str]:
    admin_role = get_or_create_admin_role(db)
    user_in = UserCreate(username="admin",
                         firstname="Admin",
                         lastname="ADMIN",
                         email=random_email(),
                         password=random_lower_string(),
                         role_id=admin_role.id)
    user = users.create_user(db=db, user=user_in)
    return user, user_in.password


def create_platform_user(db: Session) ->  Tuple[User, str]:
    platform_role = get_or_create_platform_role(db=db)
    platform = create_platform(db=db, name="Platform")
    user_in = UserCreate(username="platform",
                         firstname="Platform",
                         lastname="PLATFORM",
                         email=random_email(),
                         password=random_lower_string(),
                         role_id=platform_role.id,
                         platform_id=platform.id)
    user = users.create_user(db=db, user=user_in)
    return user, user_in.password


def get_main_platform_user(db: Session) -> User:
    return users.get_user_by_username(db=db, username="platform")


def retrieve_all_entity_types(db: Session) -> List[EntityType]:
    return entities.get_entity_types(db=db)


def create_random_entity_type(name: str, db: Session) -> EntityType:
    type_in = EntityTypeCreate(name=name)
    return entities.create_entity_type(db=db, entity_type=type_in)


def create_random_entity(name: str, db: Session) -> None:
    entity_type_name = f"type_{name}"
    entity_type = create_random_entity_type(name=entity_type_name, db=db)
    entity_in = EntityCreate(name=name, entity_type_id=entity_type.id)
    entities.create_entity(db=db, entity=entity_in)


def get_authorization_headers(client: TestClient, db: Session, for_admin: bool = False) -> dict[str, str]:
    if for_admin:
        user, password = create_admin_user(db)
    else:
        user, password = create_platform_user(db)

    login_data = {"username": user.username,
                  "password": password,
                  }
    response = client.post("/auth/login",
                           data=login_data,
                           headers={'Content-Type': "application/x-www-form-urlencoded"})
    login_response = response.json()
    token = login_response["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers

def create_access_key(db: Session, platform_id: str):
    key = AccessKeyCreate(platform_id=platform_id)
    return access_keys.create_access_key(db=db, access_key=key)
