from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.crud import projects, regulatory_frameworks
from platform_registry import schemas
from platform_registry.api import deps
from platform_registry.core import database

router = APIRouter()
frameworks_router = APIRouter(prefix="/frameworks")


@router.get("/", response_model=list[schemas.ProjectWithDetails])
async def get_projects(skip: int = 0,
                       limit: int = 10,
                       db: Session = Depends(database.get_db),
                       user: schemas.User = Depends(deps.either_platform_or_admin)):
    return projects.get_projects(db, projects_reader=user, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=schemas.ProjectWithDetails)
async def get_project(project_id: str,
                      db: Session = Depends(database.get_db),
                      user: schemas.User = Depends(deps.either_platform_or_admin)):
    project = projects.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if user.role.is_platform and user.platform_id != project.owner_platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project does not belong to Platform")
    return project


@router.post("/", response_model=schemas.ProjectWithDetails, status_code=status.HTTP_201_CREATED)
async def create_project(project: schemas.ProjectCreate,
                         db: Session = Depends(database.get_db),
                         user: schemas.User = Depends(deps.platform_user)):
    """
    only a platform user account can create projects
    """
    return projects.create_project(db=db, project=project, user=user)


@router.patch("/{project_id}", response_model=schemas.ProjectWithDetails)
async def patch_project(project_id: str,
                        project_in: schemas.ProjectPatch,
                        db: Session = Depends(database.get_db),
                        projects_manager: schemas.User = Depends(deps.platform_user)):
    if project_in.owner_platform_id != projects_manager.platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Project owned by another platform")
    project = projects.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return projects.update_project(db=db, project=project, project_in=project_in)


@router.post("/{project_id}/share", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
async def share_project(project_id: str,
                        share_with: schemas.ProjectShare,
                        db: Session = Depends(database.get_db),
                        user: schemas.User = Depends(deps.platform_user)):
    project = projects.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_platform_id != user.platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can not share this project as it is owned by another platform")
    return projects.share_project(db=db, project=project, share_with=share_with)


@frameworks_router.get("/", response_model=list[schemas.RegulatoryFramework])
async def get_regulatory_frameworks(skip: int = 0,
                                    limit: int = 10,
                                    db: Session = Depends(database.get_db),
                                    user: schemas.User = Depends(deps.either_platform_or_admin)):
    return regulatory_frameworks.get_regulatory_frameworks(db, skip=skip, limit=limit)


@frameworks_router.get("/{framework_id}", response_model=schemas.RegulatoryFramework)
async def get_regulatory_framework(regulatory_framework_id: str,
                                   db: Session = Depends(database.get_db),
                                   user: schemas.User = Depends(deps.either_platform_or_admin)):
    db_regulatory_framework = regulatory_frameworks.get_regulatory_framework(db, framework_id=regulatory_framework_id)
    if db_regulatory_framework is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RegulatoryFramework not found")
    return db_regulatory_framework


@frameworks_router.post("/", response_model=schemas.RegulatoryFramework, status_code=status.HTTP_201_CREATED)
async def create_regulatory_framework(regulatory_framework: schemas.RegulatoryFrameworkCreate,
                                      db: Session = Depends(database.get_db),
                                      user: schemas.User = Depends(deps.registry_admin_user)):
    return regulatory_frameworks.create_regulatory_framework(db=db, regulatory_framework=regulatory_framework)


@frameworks_router.patch("/{framework_id}", response_model=schemas.RegulatoryFramework)
async def patch_regulatory_framework(framework_id: str,
                                     framework_in: schemas.RegulatoryFrameworkPatch,
                                     db: Session = Depends(database.get_db),
                                     user: schemas.User = Depends(deps.registry_admin_user)):
    framework = regulatory_frameworks.get_regulatory_framework(db, framework_id=framework_id)
    if not framework:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulatory Framework not found")
    return regulatory_frameworks.update_regulatory_framework(db=db,
                                                             framework=framework,
                                                             framework_in=framework_in)

router.include_router(frameworks_router)
