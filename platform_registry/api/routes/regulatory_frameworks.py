from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.crud import regulatory_frameworks
from platform_registry import schemas
from platform_registry.api import deps
from platform_registry.core import database

router = APIRouter()


@router.get("/", response_model=list[schemas.RegulatoryFramework])
async def get_regulatory_frameworks(skip: int = 0,
                                    limit: int = 10,
                                    db: Session = Depends(database.get_db),
                                    user: schemas.User = Depends(deps.either_platform_or_admin)):
    return regulatory_frameworks.get_regulatory_frameworks(db, skip=skip, limit=limit)


@router.get("/{regulatory_framework_id}", response_model=schemas.RegulatoryFramework)
async def get_regulatory_framework(regulatory_framework_id: str,
                                   db: Session = Depends(database.get_db),
                                   user: schemas.User = Depends(deps.either_platform_or_admin)):
    db_regulatory_framework = regulatory_frameworks.get_regulatory_framework(db, framework_id=regulatory_framework_id)
    if db_regulatory_framework is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RegulatoryFramework not found")
    return db_regulatory_framework


@router.post("/", response_model=schemas.RegulatoryFramework)
async def create_regulatory_framework(regulatory_framework: schemas.RegulatoryFrameworkCreate,
                                      db: Session = Depends(database.get_db),
                                      user: schemas.User = Depends(deps.registry_admin_user)):
    return regulatory_frameworks.create_regulatory_framework(db=db, regulatory_framework=regulatory_framework)


@router.patch("/{framework_id}", response_model=schemas.RegulatoryFramework)
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

