import os
from datetime import datetime
from typing import Union

from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import is_

from platform_registry.core.security import get_password_hash
from platform_registry.models import User
from platform_registry.schemas import RegularUserCreate, AdminUserCreate, PlatformUserCreate, Role


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def get_user_by_username(db: Session, username: str, user: User = None):
    user_found = db.query(User).filter(User.username == username).first()
    if user and user.role.is_platform and user_found.role is not None:
        return None
    return user_found



def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session):
    return db.query(User).all()


def get_regular_users(db: Session):
    # /!\ regular user must have no role attached to them
    return db.query(User).filter(is_(User.role, None)).all()


def get_platform_accounts_users(db: Session):
    return db.query(User).filter(User.role.is_platform).all()


def get_registry_admins_users(db: Session):
    return db.query(User).filter(User.role.is_registry_admin).all()


def create_user(db: Session, user: Union[RegularUserCreate,
                                         AdminUserCreate,
                                         PlatformUserCreate]):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_admin_user(db: Session, role: Role) -> User:
    admin_user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if admin_user:
        return admin_user
    user_in = AdminUserCreate(username=ADMIN_USERNAME,
                              firstname='Admin',
                              lastname='ADMIN',
                              email='admin.admin@registry.fr',
                              hashed_password=get_password_hash(ADMIN_PASSWORD),
                              role_id=role.id)
    return create_user(db=db, user=user_in)


def update_user_last_login(db: Session, user):
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    return user
