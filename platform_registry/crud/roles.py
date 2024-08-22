from sqlalchemy.orm import Session

from platform_registry.schemas import RoleCreate
from platform_registry.models import Role

DEFAULT_REGISTRY_ADMIN_ROLE_PROPS: dict[str, bool] = dict(manage_users=True,
                                                          manage_roles=True,
                                                          manage_entities=True,
                                                          manage_regulatory_frameworks=True,
                                                          manage_access_keys=True,
                                                          manage_platforms=True,
                                                          manage_projects=False,
                                                          manage_projects_membership=False)
DEFAULT_PLATFORM_ROLE_PROPS: dict[str, bool] = dict(manage_users=False,
                                                    manage_roles=False,
                                                    manage_entities=False,
                                                    manage_regulatory_frameworks=False,
                                                    manage_access_keys=True,
                                                    manage_platforms=True,
                                                    manage_projects=True,
                                                    manage_projects_membership=True)


def get_role_by_id(db: Session, role_id: str):
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()


def get_main_admin_role(db: Session):
    return db.query(Role).filter(Role.is_registry_admin).first()


def get_main_platform_role(db: Session):
    return db.query(Role).filter(Role.is_platform).first()


def complete_role_initial_data(role: RoleCreate) -> dict:
    properties = role.is_platform and DEFAULT_PLATFORM_ROLE_PROPS or DEFAULT_REGISTRY_ADMIN_ROLE_PROPS
    return {**role.model_dump(), **properties}


def create_role(db: Session, role: RoleCreate):
    completed_role = complete_role_initial_data(role=role)
    db_role = Role(**completed_role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_roles(db: Session):
    return db.query(Role).all()
