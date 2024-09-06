from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from platform_registry.core.security import get_password_hash
from platform_registry.models import Platform, User
from platform_registry.schemas import PlatformCreate, PlatformUserCreateCreate, AccessKeyCreate, PlatformPatch
from platform_registry.services import roles, users
from platform_registry.services.access_keys import create_access_key


def get_platforms(db: Session, user: User, to_share_project=False):
    platforms_filter = []
    if user.role.is_platform:
        if to_share_project:
            platforms_filter.append(Platform.id != user.platform_id)
        else:
            platforms_filter.append(Platform.id == user.platform_id)
    return db.query(Platform).filter(*platforms_filter).all()


def get_platform_by_id(db: Session, platform_id: str):
    return db.query(Platform).filter(Platform.id == platform_id).first()


def create_platform(db: Session, platform: PlatformCreate):
    db_platform = Platform(name=platform.name)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform


def setup_platform(db: Session, platform: PlatformCreate):
    new_platform = create_platform(db=db, platform=platform)
    ak = create_access_key(db=db, access_key=AccessKeyCreate(platform_id=new_platform.id))
    platform_role = roles.get_platform_role(db=db)
    username = platform.name.replace(' ', '-').lower()
    platform_user = PlatformUserCreateCreate(username=username,
                                             expiration_date=datetime.now() + timedelta(days=365),
                                             hashed_password=get_password_hash(ak.key),
                                             role_id=platform_role.id,
                                             platform_id=new_platform.id)
    users.create_user(db=db, user=platform_user)
    return new_platform


def update_platform(db: Session, platform: Platform, platform_in: PlatformPatch):
    platform_data = platform_in.model_dump(exclude_unset=True,
                                           exclude_none=True)
    for k, v in platform_data.items():
        setattr(platform, k, v)
    db.commit()
    db.refresh(platform)
    return platform