from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from platform_registry import crud, schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.RegulatoryFramework)
async def create_regulatory_framework(regulatory_framework: schemas.RegulatoryFrameworkCreate, db: Session = Depends(database.get_db)):
    return crud.create_regulatory_framework(db=db, regulatory_framework=regulatory_framework)


@router.get("/{regulatory_framework_id}", response_model=schemas.RegulatoryFramework)
async def read_regulatory_framework(regulatory_framework_id: int, db: Session = Depends(database.get_db)):
    db_regulatory_framework = crud.get_regulatory_framework(db, regulatory_framework_id=regulatory_framework_id)
    if db_regulatory_framework is None:
        raise HTTPException(status_code=404, detail="RegulatoryFramework not found")
    return db_regulatory_framework


@router.get("/", response_model=list[schemas.RegulatoryFramework])
async def read_regulatory_frameworks(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    regulatory_frameworks = crud.get_regulatory_frameworks(db, skip=skip, limit=limit)
    return regulatory_frameworks
