from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from platform_registry.services import roles
from platform_registry import schemas
from platform_registry.api.deps import registry_admin_user
from platform_registry.core import database


router = APIRouter(dependencies=[Depends(registry_admin_user)])


@router.get("/", response_model=list[schemas.Role])
async def get_roles(db: Session = Depends(database.get_db)):
    return roles.get_roles(db)


@router.get("/{role_id}", response_model=schemas.Role)
async def get_role(role_id: str, db: Session = Depends(database.get_db)):
    db_role = roles.get_role_by_id(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role


@router.post("/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
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
