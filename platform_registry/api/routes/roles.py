from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from platform_registry.services import roles
from platform_registry import schemas
from platform_registry.api.deps import registry_admin_user
from platform_registry.core import database


router = APIRouter(dependencies=[Depends(registry_admin_user)])


@router.get(path="/", response_model=list[schemas.Role],
            description="Returns mainly two major roles: `Registry Admin` and `Platform`")
async def get_roles(db: Session = Depends(database.get_db)):
    return roles.get_roles(db)


@router.post(path="/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED,
             description="Two roles are expected to be created: `Registry Admin` and `Platform`. "
                         "No further roles are allowed to be created")
async def create_role(role: schemas.RoleCreate, db: Session = Depends(database.get_db)):
    msg = "Role must be either Platform or Registry Admin"
    if not (role.is_platform or role.is_registry_admin):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    if role.is_platform and role.is_registry_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{msg}, not both")

    role_type = role.is_platform and "Platform" or "Registry Admin"
    try:
        role = roles.create_role(db=db, role=role)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"A role of type '{role_type}' has been previously added")
    return role
