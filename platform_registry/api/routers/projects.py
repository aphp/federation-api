from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from platform_registry import crud, schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.Project)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    return crud.create_project(db=db, project=project)


@router.get("/{project_id}", response_model=schemas.Project)
async def read_project(project_id: int, db: Session = Depends(database.get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.get("/", response_model=list[schemas.Project])
async def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects
