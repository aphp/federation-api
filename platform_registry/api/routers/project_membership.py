from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from platform_registry import crud, schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.ProjectMembership)
async def create_project_membership(project_membership: schemas.ProjectMembershipCreate, db: Session = Depends(database.get_db)):
    return crud.create_project_membership(db=db, project_membership=project_membership)


@router.get("/{project_membership_id}", response_model=schemas.ProjectMembership)
async def read_project_membership(project_membership_id: int, db: Session = Depends(database.get_db)):
    db_project_membership = crud.get_project_membership(db, project_membership_id=project_membership_id)
    if db_project_membership is None:
        raise HTTPException(status_code=404, detail="ProjectMembership not found")
    return db_project_membership


@router.get("/", response_model=list[schemas.ProjectMembership])
async def read_project_memberships(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    project_memberships = crud.get_project_memberships(db, skip=skip, limit=limit)
    return project_memberships
