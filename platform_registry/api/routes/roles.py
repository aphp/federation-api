from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.crud import roles
from platform_registry import schemas
from platform_registry.api.deps import registry_admin_user
from platform_registry.core import database


router = APIRouter(dependencies=[Depends(registry_admin_user)])


@router.get("/", response_model=list[schemas.Role])
async def get_roles(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return roles.get_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=schemas.Role)
async def get_role(role_id: str, db: Session = Depends(database.get_db)):
    db_role = roles.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role


@router.post("/", response_model=schemas.Role)
async def create_role(role: schemas.RoleCreate, db: Session = Depends(database.get_db)):
    if not (role.is_platform or role.is_registry_admin):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be either Platform or Registry Admin")
    return roles.create_role(db=db, role=role)
