from sqlalchemy.orm import Session

from platform_registry.models import Platform
from platform_registry.schemas import User, PlatformCreate


def get_platforms(db: Session, user: User):
    platforms_filter = []
    if user.role.is_platform:
        platforms_filter.append(Platform.id == user.platform_id)
    return db.query(Platform).filter(*platforms_filter).all()


def get_platform(db: Session, platform_id: str):
    return db.query(Platform).filter(Platform.id == platform_id).first()


def create_platform(db: Session, platform: PlatformCreate):
    db_platform = Platform(name=platform.name)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform

