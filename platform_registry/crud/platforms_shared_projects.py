from sqlalchemy.orm import Session

from platform_registry import models, schemas


def get_platform_shared_project(db: Session, platform_id: str, project_id: str):
    return db.query(models.PlatformsSharedProjectsRel).filter(
        models.PlatformsSharedProjectsRel.platform_id == platform_id,
        models.PlatformsSharedProjectsRel.project_id == project_id
    ).first()


def create_platform_shared_project(db: Session, platform_shared_project: schemas.PlatformSharedProjectsCreate):
    db_platform_shared_project = models.PlatformsSharedProjectsRel(
        platform_id=platform_shared_project.platform_id,
        project_id=platform_shared_project.project_id
    )
    db.add(db_platform_shared_project)
    db.commit()
    db.refresh(db_platform_shared_project)
    return db_platform_shared_project


def get_platform_shared_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.PlatformsSharedProjectsRel).offset(skip).limit(limit).all()
