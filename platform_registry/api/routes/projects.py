from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.crud import projects
from platform_registry import schemas
from platform_registry.api import deps
from platform_registry.core import database

router = APIRouter()


@router.get("/", response_model=list[schemas.Project])
async def get_projects(skip: int = 0,
                       limit: int = 10,
                       db: Session = Depends(database.get_db),
                       user: schemas.User = Depends(deps.either_platform_or_admin)):
    return projects.get_projects(db, projects_reader=user, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=schemas.Project)
async def get_project(project_id: str,
                      db: Session = Depends(database.get_db),
                      user: schemas.User = Depends(deps.either_platform_or_admin)):
    project = projects.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if user.role.is_platform and project.platform_owner_id != user.platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project does not belong to Platform")
    return project


@router.post("/", response_model=schemas.Project)
async def create_project(project: schemas.ProjectCreate,
                         db: Session = Depends(database.get_db),
                         projects_manager: schemas.User = Depends(deps.projects_manager)):
    """
    only a platform user account can create projects
    """
    if project.owner_platform_id != projects_manager.platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Project owned by another platform")
    return projects.create_project(db=db, project=project)


@router.patch("/{project_id}", response_model=schemas.Project)
async def patch_project(project_id: str,
                        project_in: schemas.ProjectPatch,
                        db: Session = Depends(database.get_db),
                        projects_manager: schemas.User = Depends(deps.projects_manager)):
    if project_in.owner_platform_id != projects_manager.platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Project owned by another platform")
    project = projects.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return projects.update_project(db=db, project=project, project_in=project_in)

