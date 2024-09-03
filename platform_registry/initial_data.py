import logging

from sqlalchemy.orm import Session

from models import Role
from services import roles, users
from schemas import RoleCreate
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


def create_platform_role(db: Session):
    platform_role = db.query(Role).filter(Role.is_platform).first()
    if not platform_role:
        role_in = RoleCreate(name='Platform',
                             is_registry_admin=False,
                             is_platform=True)
        roles.create_role(db=db, role=role_in)


def load_initial_data(db: Session) -> None:
    admin_role = create_admin_role(db=db)
    users.create_admin_user(db=db, role=admin_role)
    logger.info(f"Admin role and user created {'...'*5}OK")
    create_platform_role(db=db)
    logger.info(f"Platform role created {'...'*5}OK")



def main() -> None:
    load_initial_data(db=next(get_db()))


if __name__ == "__main__":
    main()
