from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from platform_registry.crud import platforms
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.Platform)
async def create_platform(platform: schemas.PlatformCreate, db: Session = Depends(database.get_db)):
    return platforms.create_platform(db=db, platform=platform)


@router.get("/{platform_id}", response_model=schemas.Platform)
async def get_platform(platform_id: str, db: Session = Depends(database.get_db)):
    db_platform = platforms.get_platform(db, platform_id=platform_id)
    if db_platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return db_platform


@router.get("/", response_model=list[schemas.Platform])
async def get_platforms(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return platforms.get_platforms(db, skip=skip, limit=limit)
