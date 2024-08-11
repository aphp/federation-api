from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from platform_registry import schemas, models
from platform_registry.core.config import settings
from platform_registry.utils import generate_key


def get_access_keys(db: Session, keys_reader: schemas.User, skip: int = 0, limit: int = 10):
    keys_filter = {}
    if keys_reader.role.is_platform:
        keys_filter = {"platform_id": keys_reader.platform_id}
    return db.query(models.AccessKey).filter(and_(**keys_filter)).offset(skip).limit(limit).all()


def get_access_key(db: Session, key_id: str):
    return db.query(models.AccessKey).filter(models.AccessKey.id == key_id).first()


def create_access_key(db: Session, access_key: schemas.AccessKeyCreate):
    now = datetime.now()
    year_month = now.strftime('%Y%m')
    key_name = f"{access_key.platform_id[:8]}_{year_month}_key"
    key = models.AccessKey(name=key_name,
                           key=generate_key(),
                           start_datetime=now,
                           end_datetime=now + timedelta(days=settings.ACCESS_KEY_LIFESPAN_DAYS),
                           platform_id=access_key.platform_id)
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


def valid_key_exists(db: Session, platform_id: str) -> bool:
    return db.query(models.AccessKey).filter(models.AccessKey.platform_id == platform_id,
                                             models.AccessKey.start_datetime <= datetime.now(),
                                             models.AccessKey.end_datetime > datetime.now())\
                                     .first() is not None


def check_access_key_validity(db: Session, start: datetime, end: datetime) -> Tuple[bool, str]:
    valid, msg = True, ""
    if end <= start:
        valid, msg = False, "End date must be greater than start date"
    return valid, msg


def update_access_key(*, db: Session, key: models.AccessKey, key_in: schemas.AccessKeyPatch):
    key_data = key_in.model_dump()
    for key, value in key_data.items():
        setattr(key, key, value)
    db.commit()
    db.refresh(key)
    return key
