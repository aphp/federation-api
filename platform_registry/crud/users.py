from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import is_

from platform_registry import models, schemas
from platform_registry.core.security import get_password_hash
from platform_registry.crud.roles import get_role


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
                          hashed_password=get_password_hash(user.password),
                          role_id=user.role_id,
                          platform_id=user.platform_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_regular_users(db: Session, skip: int = 0, limit: int = 10):
    # todo: try .filter(models.User.role is None)
    return db.query(models.User).filter(is_(models.User.role, None))\
                                .offset(skip).limit(limit).all()


def get_platform_accounts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).filter(models.User.role.is_platform)\
                                .offset(skip).limit(limit).all()


def get_registry_admins_accounts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).filter(models.User.role.is_registry_admin)\
                                .offset(skip).limit(limit).all()


def check_user_against_linked_role(db: Session, user: schemas.UserCreate):
    role = get_role(db, user.role_id)
    valid, msg = True, ""
    if role:
        if role.is_platform and user.platform_id is None:
            valid = False
            msg = "The user is a Platform account but no linked platform is provided"
        if role.is_registry_admin and user.platform_id is not None:
            valid = False
            msg = "The user is a Registry Admin account but a linked platform is provided"
    return valid, msg
