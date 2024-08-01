from sqlalchemy.orm import Session

from platform_registry import models, schemas

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


def get_role(db: Session, role_id: str):
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    return db.query(models.Role).filter(models.Role.name == name).first()


def complete_role_initial_data(role: schemas.RoleCreate) -> dict:
    properties = role.is_platform and DEFAULT_PLATFORM_ROLE_PROPS or DEFAULT_REGISTRY_ADMIN_ROLE_PROPS
    return {**role.model_dump(), **properties}


def create_role(db: Session, role: schemas.RoleCreate):
    completed_role = complete_role_initial_data(role=role)
    db_role = models.Role(**completed_role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_roles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Role).offset(skip).limit(limit).all()
