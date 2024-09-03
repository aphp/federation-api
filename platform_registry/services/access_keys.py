import secrets
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.orm import Session

from platform_registry.core.config import settings
from platform_registry.models import AccessKey
from platform_registry.schemas import AccessKeyPatch, AccessKeyCreate


def generate_key() -> str:
    return secrets.token_urlsafe(32)


def get_access_keys(db: Session):
    return db.query(AccessKey).all()


def get_access_key_by_id(db: Session, key_id: str):
    return db.query(AccessKey).filter(AccessKey.id == key_id).first()


def get_platform_access_keys(db: Session, platform_id: str):
    return db.query(AccessKey).filter(AccessKey.platform_id == platform_id)\
                              .all()


def get_platform_current_valid_key(db: Session, platform_id: str):
    return db.query(AccessKey).filter(AccessKey.platform_id == platform_id,
                                      AccessKey.start_datetime <= datetime.now(),
                                      AccessKey.end_datetime > datetime.now())\
                              .first()


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


def check_access_key_validity(key_in: AccessKeyPatch) -> Tuple[bool, str]:
    if key_in.start_datetime and key_in.end_datetime and key_in.start_datetime >= key_in.end_datetime:
        return False, "End date must be greater than start date"
    return True, ""


def update_access_key(db: Session, key: AccessKey, key_in: AccessKeyPatch):
    key_data = key_in.model_dump(exclude_unset=True,
                                 exclude_none=True)
    for k, v in key_data.items():
        setattr(key, k, v)
    db.commit()
    db.refresh(key)
    return key

def archive_access_key(db: Session, key: AccessKey):
    now = datetime.now()
    key.end_datetime = now
    key.deleted_at = now
    db.commit()
    db.refresh(key)
    return key
