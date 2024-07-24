from sqlalchemy.orm import Session
from platform_registry import models, schemas
from platform_registry.utils import get_password_hash


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username,
                          email=user.email,
                          firstname=user.firstname,
                          lastname=user.lastname,
                          expiration_date=user.expiration_date,
                          hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    return db.query(models.Role).filter(models.Role.name == name).first()


def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_roles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Role).offset(skip).limit(limit).all()


def get_entity_type(db: Session, entity_type_id: int):
    return db.query(models.EntityType).filter(models.EntityType.id == entity_type_id).first()


def create_entity_type(db: Session, entity_type: schemas.EntityTypeCreate):
    db_entity_type = models.EntityType(name=entity_type.name)
    db.add(db_entity_type)
    db.commit()
    db.refresh(db_entity_type)
    return db_entity_type


def get_entity_types(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.EntityType).offset(skip).limit(limit).all()


def get_regulatory_framework(db: Session, regulatory_framework_id: int):
    return db.query(models.RegulatoryFramework).filter(models.RegulatoryFramework.id == regulatory_framework_id).first()


def create_regulatory_framework(db: Session, regulatory_framework: schemas.RegulatoryFrameworkCreate):
    db_regulatory_framework = models.RegulatoryFramework(
        name=regulatory_framework.name,
        description_url=regulatory_framework.description_url
    )
    db.add(db_regulatory_framework)
    db.commit()
    db.refresh(db_regulatory_framework)
    return db_regulatory_framework


def get_regulatory_frameworks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.RegulatoryFramework).offset(skip).limit(limit).all()


def get_entity(db: Session, entity_id: int):
    return db.query(models.Entity).filter(models.Entity.id == entity_id).first()


def create_entity(db: Session, entity: schemas.EntityCreate):
    db_entity = models.Entity(
        name=entity.name,
        entity_type_id=entity.entity_type_id
    )
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def get_entities(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Entity).offset(skip).limit(limit).all()


def get_project_membership(db: Session, project_membership_id: int):
    return db.query(models.ProjectMembership).filter(models.ProjectMembership.id == project_membership_id).first()


def create_project_membership(db: Session, project_membership: schemas.ProjectMembershipCreate):
    db_project_membership = models.ProjectMembership(
        entity_id=project_membership.entity_id,
        project_id=project_membership.project_id,
        user_id=project_membership.user_id,
        functional_role=project_membership.functional_role
    )
    db.add(db_project_membership)
    db.commit()
    db.refresh(db_project_membership)
    return db_project_membership


def get_project_memberships(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ProjectMembership).offset(skip).limit(limit).all()


def get_project_regulatory_framework(db: Session, project_id: int, regulatory_framework_id: int):
    return db.query(models.ProjectRegulatoryFramework).filter(
        models.ProjectRegulatoryFramework.project_id == project_id,
        models.ProjectRegulatoryFramework.regulatory_framework_id == regulatory_framework_id
    ).first()


def create_project_regulatory_framework(db: Session, project_regulatory_framework: schemas.ProjectRegulatoryFrameworkCreate):
    db_project_regulatory_framework = models.ProjectRegulatoryFramework(
        project_id=project_regulatory_framework.project_id,
        regulatory_framework_id=project_regulatory_framework.regulatory_framework_id
    )
    db.add(db_project_regulatory_framework)
    db.commit()
    db.refresh(db_project_regulatory_framework)
    return db_project_regulatory_framework


def get_project_regulatory_frameworks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ProjectRegulatoryFramework).offset(skip).limit(limit).all()


def get_platform(db: Session, platform_id: int):
    return db.query(models.Platform).filter(models.Platform.id == platform_id).first()


def create_platform(db: Session, platform: schemas.PlatformCreate):
    db_platform = models.Platform(name=platform.name)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform


def get_platforms(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Platform).offset(skip).limit(limit).all()


def get_platform_shared_project(db: Session, platform_id: int, project_id: int):
    return db.query(models.PlatformSharedProjects).filter(
        models.PlatformSharedProjects.platform_id == platform_id,
        models.PlatformSharedProjects.project_id == project_id
    ).first()


def create_platform_shared_project(db: Session, platform_shared_project: schemas.PlatformSharedProjectsCreate):
    db_platform_shared_project = models.PlatformSharedProjects(
        platform_id=platform_shared_project.platform_id,
        project_id=platform_shared_project.project_id
    )
    db.add(db_platform_shared_project)
    db.commit()
    db.refresh(db_platform_shared_project)
    return db_platform_shared_project


def get_platform_shared_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.PlatformSharedProjects).offset(skip).limit(limit).all()


def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        code=project.code,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Project).offset(skip).limit(limit).all()
