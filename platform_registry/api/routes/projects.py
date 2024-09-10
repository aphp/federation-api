from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.models import User
from platform_registry.services import projects, regulatory_frameworks as reg_frameworks
from platform_registry import schemas
from platform_registry.api import deps
from platform_registry.core import database

router = APIRouter()
frameworks_router = APIRouter(prefix="/frameworks")


@router.get(path="/", response_model=list[schemas.ProjectWithDetails],
            summary="List owned projects and those shared by other platforms "
                    "with details over involved users and entities")
async def get_projects(db: Session = Depends(database.get_db),
                       user: User = Depends(deps.either_platform_or_admin)):
    return projects.get_projects(db, user=user)


@router.get(path="/{project_id}", response_model=schemas.ProjectWithDetails)
async def get_project(project_id: str,
                      db: Session = Depends(database.get_db),
                      user: User = Depends(deps.either_platform_or_admin)):
    project = projects.get_project_by_id(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if user.role.is_platform and \
       not projects.platform_can_access_project(platform=user.platform, target_project=project):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project does not belong to Platform")
    return project


@router.post(path="/", response_model=schemas.ProjectWithDetails, status_code=status.HTTP_201_CREATED,
             summary="Create a new project and optionally assign users and entities",
             description="As a **Platform User**, the project being created will be auto-attached to your platform.")
async def create_project(project: schemas.ProjectCreate,
                         db: Session = Depends(database.get_db),
                         user: User = Depends(deps.platform_user)):
    return projects.create_project(db=db, project=project, platform_id=user.platform_id)


@router.patch(path="/{project_id}", response_model=schemas.ProjectWithDetails,
              summary="Update project details, related regulatory frameworks, users and entities",)
async def patch_project(project_id: str,
                        project_in: schemas.ProjectPatch,
                        db: Session = Depends(database.get_db),
                        user: User = Depends(deps.platform_user)):
    project = projects.get_project_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if not projects.platform_can_edit_project(db=db, platform=user.platform, target_project=project):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This project is owned by another platform or you are not allowed to edit it")
    return projects.update_project(db=db, project=project, project_in=project_in)


@router.post(path="/{project_id}/share", response_model=schemas.ProjectShareResult,
             description="Takes recipient platforms list with a boolean access mode `readonly`.\n\n"
                         "* If unset, recipient platforms will have readonly access by default to the project.\n\n"
                         "* With `readonly` set to `false`, the recipient platform will be able to edit the project details.")
async def share_project(project_id: str,
                        share_with: schemas.ProjectShare,
                        db: Session = Depends(database.get_db),
                        user: User = Depends(deps.platform_user)):
    project = projects.get_project_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if not projects.platform_can_share_project(platform=user.platform, project=project):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can not share this project as it is owned by another platform")
    return projects.share_project(db=db, project=project, share_with=share_with)


@frameworks_router.get(path="/", response_model=list[schemas.RegulatoryFramework])
async def get_regulatory_frameworks(db: Session = Depends(database.get_db),
                                    user: User = Depends(deps.either_platform_or_admin)):
    return reg_frameworks.get_regulatory_frameworks(db)


@frameworks_router.get(path="/{framework_id}", response_model=schemas.RegulatoryFramework)
async def get_regulatory_framework(regulatory_framework_id: str,
                                   db: Session = Depends(database.get_db),
                                   user: User = Depends(deps.either_platform_or_admin)):
    db_regulatory_framework = reg_frameworks.get_regulatory_framework(db, framework_id=regulatory_framework_id)
    if db_regulatory_framework is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RegulatoryFramework not found")
    return db_regulatory_framework


@frameworks_router.post(path="/", response_model=schemas.RegulatoryFramework, status_code=status.HTTP_201_CREATED)
async def create_regulatory_framework(regulatory_framework: schemas.RegulatoryFrameworkCreate,
                                      db: Session = Depends(database.get_db),
                                      user: User = Depends(deps.registry_admin_user)):
    return reg_frameworks.create_regulatory_framework(db=db, regulatory_framework=regulatory_framework)


@frameworks_router.patch(path="/{framework_id}", response_model=schemas.RegulatoryFramework)
async def patch_regulatory_framework(framework_id: str,
                                     framework_in: schemas.RegulatoryFrameworkPatch,
                                     db: Session = Depends(database.get_db),
                                     user: User = Depends(deps.registry_admin_user)):
    framework = reg_frameworks.get_regulatory_framework(db, framework_id=framework_id)
    if not framework:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulatory Framework not found")
    return reg_frameworks.update_regulatory_framework(db=db,
                                                      framework=framework,
                                                      framework_in=framework_in)

router.include_router(frameworks_router)
