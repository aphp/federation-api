import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import User, Role
from crud import roles, users
from schemas import UserCreate, RoleCreate
from core.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_role(db: Session):
    admin_role = db.query(Role).filter(Role.is_registry_admin).first()
    if not admin_role:
        role_in = RoleCreate(name='Registry Admin',
                             is_registry_admin=True,
                             is_platform=False)
        admin_role = roles.create_role(db=db, role=role_in)
    return admin_role


def create_admin_user(db: Session, role):
    admin_username = "admin"
    user = db.query(User).filter(User.username == admin_username).first()
    if not user:
        user_in = UserCreate(username=admin_username,
                             firstname='Admin',
                             lastname='ADMIN',
                             email='admin.admin@localhost.com',
                             password='1234',
                             expiration_date=datetime.now() + timedelta(days=365),
                             role_id=role.id)
        user = users.create_user(db=db, user=user_in)


def load_init_data(db: Session) -> None:
    admin_role = create_admin_role(db=db)
    create_admin_user(db=db, role=admin_role)


def main() -> None:
    logger.info("Creating admin role and user")
    load_init_data(db=next(get_db()))
    logger.info("Admin role and user created")


if __name__ == "__main__":
    main()
