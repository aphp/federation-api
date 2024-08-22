from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.orm import Session

from platform_registry.core.config import settings
from platform_registry.schemas import AccessKey, AccessKeyPatch, AccessKeyCreate, User
from platform_registry.utils import generate_key


def get_access_keys(db: Session):
    return db.query(AccessKey).all()


def get_platform_access_keys(db: Session, keys_reader: User):
    return db.query(AccessKey).filter(AccessKey.platform_id == keys_reader.platform_id)\
                              .all()


def get_access_key(db: Session, key_id: str):
    return db.query(AccessKey).filter(AccessKey.id == key_id).first()


def create_access_key(db: Session, access_key: AccessKeyCreate):
    now = datetime.now()
    year_month = now.strftime('%Y%m')
    key_name = f"{access_key.platform_id[:8]}_{year_month}_key"
    key = AccessKey(name=key_name,
                           key=generate_key(),
                           start_datetime=now,
                           end_datetime=now + timedelta(days=settings.ACCESS_KEY_LIFESPAN_DAYS),
                           platform_id=access_key.platform_id)
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


def valid_key_exists(db: Session, platform_id: str) -> bool:
    return db.query(AccessKey).filter(AccessKey.platform_id == platform_id,
                                      AccessKey.start_datetime <= datetime.now(),
                                      AccessKey.end_datetime > datetime.now())\
                              .first() is not None


def check_access_key_validity(db: Session, start: datetime, end: datetime) -> Tuple[bool, str]:
    valid, msg = True, ""
    if end <= start:
        valid, msg = False, "End date must be greater than start date"
    return valid, msg


def update_access_key(*, db: Session, key: AccessKey, key_in: AccessKeyPatch):
    key_data = key_in.model_dump()
    for key, value in key_data.items():
        setattr(key, key, value)
    db.commit()
    db.refresh(key)
    return key
