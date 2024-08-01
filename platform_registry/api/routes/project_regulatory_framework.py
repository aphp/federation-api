from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from platform_registry.crud import projects_regulatory_frameworks as project_frameworks
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.ProjectRegulatoryFramework)
async def create_project_regulatory_framework(project_regulatory_framework: schemas.ProjectRegulatoryFrameworkCreate,
                                              db: Session = Depends(database.get_db)):
    return project_frameworks.create_project_regulatory_framework(db=db,
                                                                  project_regulatory_framework=project_regulatory_framework)


@router.get("/{project_id}/{regulatory_framework_id}", response_model=schemas.ProjectRegulatoryFramework)
async def get_project_regulatory_framework(project_id: str, regulatory_framework_id: str, db: Session = Depends(database.get_db)):
    db_project_regulatory_framework = project_frameworks.get_project_regulatory_framework(db,
                                                                                          project_id=project_id,
                                                                                          regulatory_framework_id=regulatory_framework_id)
    if db_project_regulatory_framework is None:
        raise HTTPException(status_code=404, detail="ProjectRegulatoryFramework not found")
    return db_project_regulatory_framework


@router.get("/", response_model=list[schemas.ProjectRegulatoryFramework])
async def get_project_regulatory_frameworks(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return project_frameworks.get_project_regulatory_frameworks(db, skip=skip, limit=limit)
