from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from platform_registry.crud import platforms_shared_projects
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.PlatformSharedProjects)
def create_platform_shared_project(platform_shared_project: schemas.PlatformSharedProjectsCreate, db: Session = Depends(database.get_db)):
    return platforms_shared_projects.create_platform_shared_project(db=db, platform_shared_project=platform_shared_project)


@router.get("/{platform_id}/{project_id}", response_model=schemas.PlatformSharedProjects)
def read_platform_shared_project(platform_id: str, project_id: str, db: Session = Depends(database.get_db)):
    db_platform_shared_project = platforms_shared_projects.get_platform_shared_project(db, platform_id=platform_id, project_id=project_id)
    if db_platform_shared_project is None:
        raise HTTPException(status_code=404, detail="PlatformSharedProject not found")
    return db_platform_shared_project


@router.get("/", response_model=list[schemas.PlatformSharedProjects])
def read_platform_shared_projects(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return platforms_shared_projects.get_platform_shared_projects(db, skip=skip, limit=limit)
