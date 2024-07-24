from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from platform_registry import crud, schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.ProjectRegulatoryFramework)
async def create_project_regulatory_framework(project_regulatory_framework: schemas.ProjectRegulatoryFrameworkCreate, db: Session = Depends(database.get_db)):
    return crud.create_project_regulatory_framework(db=db, project_regulatory_framework=project_regulatory_framework)


@router.get("/{project_id}/{regulatory_framework_id}", response_model=schemas.ProjectRegulatoryFramework)
async def read_project_regulatory_framework(project_id: int, regulatory_framework_id: int, db: Session = Depends(database.get_db)):
    db_project_regulatory_framework = crud.get_project_regulatory_framework(db, project_id=project_id, regulatory_framework_id=regulatory_framework_id)
    if db_project_regulatory_framework is None:
        raise HTTPException(status_code=404, detail="ProjectRegulatoryFramework not found")
    return db_project_regulatory_framework


@router.get("/", response_model=list[schemas.ProjectRegulatoryFramework])
async def read_project_regulatory_frameworks(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    project_regulatory_frameworks = crud.get_project_regulatory_frameworks(db, skip=skip, limit=limit)
    return project_regulatory_frameworks
