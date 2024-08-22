from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import is_

from platform_registry.core.security import get_password_hash
from platform_registry.crud import roles
from platform_registry.models import User
from platform_registry.schemas import UserCreate


def get_user_by_username(db: Session, username: str, user: User = None):
    user_found = db.query(User).filter(User.username == username).first()
    if user and user.role.is_platform and user_found.role is not None:
        return None
    return user_found



def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    db_user = User(username=user.username,
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


def get_all_users(db: Session):
    return db.query(User).all()


def get_regular_users(db: Session):
    # /!\ regular user must have no role attached to them
    return db.query(User).filter(is_(User.role, None))\
                         .all()


def get_platform_accounts_users(db: Session):
    return db.query(User).filter(User.role.is_platform)\
                         .all()


def get_registry_admins_users(db: Session):
    return db.query(User).filter(User.role.is_registry_admin)\
                         .all()


def check_user_against_linked_role(db: Session, user: UserCreate):
    role = roles.get_role_by_id(db, user.role_id)
    valid, msg = True, ""
    if role:
        if role.is_platform and user.platform_id is None:
            valid = False
            msg = "The user is a Platform account but no linked platform is provided"
        if role.is_registry_admin and user.platform_id is not None:
            valid = False
            msg = "The user is a Registry Admin account but a linked platform is provided"
    elif user.platform_id:
        valid = False
        msg = "The user is a linked to a platform but missing the Platform role"
    return valid, msg


def update_user_last_login(db: Session, user):
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    return user
