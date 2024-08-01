from sqlalchemy.orm import Session

from platform_registry import models, schemas


def get_platform(db: Session, platform_id: str):
    return db.query(models.Platform).filter(models.Platform.id == platform_id).first()


def create_platform(db: Session, platform: schemas.PlatformCreate):
    db_platform = models.Platform(name=platform.name)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform


def get_platforms(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Platform).offset(skip).limit(limit).all()
