from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from platform_registry import crud, schemas
from platform_registry.core import database


router = APIRouter()


@router.post("/", response_model=schemas.Role)
async def create_role(role: schemas.RoleCreate, db: Session = Depends(database.get_db)):
    db_role = crud.get_role_by_name(db, name=role.name)
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    return crud.create_role(db=db, role=role)


@router.get("/{role_id}", response_model=schemas.Role)
async def read_role(role_id: int, db: Session = Depends(database.get_db)):
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.get("/", response_model=list[schemas.Role])
async def read_roles(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles
