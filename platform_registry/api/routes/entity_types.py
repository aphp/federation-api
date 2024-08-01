from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from platform_registry.crud import entities
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.EntityType)
async def create_entity_type(entity_type: schemas.EntityTypeCreate, db: Session = Depends(database.get_db)):
    return entities.create_entity_type(db=db, entity_type=entity_type)


@router.get("/{entity_type_id}", response_model=schemas.EntityType)
async def get_entity_type(entity_type_id: str, db: Session = Depends(database.get_db)):
    db_entity_type = entities.get_entity_type(db, entity_type_id=entity_type_id)
    if db_entity_type is None:
        raise HTTPException(status_code=404, detail="EntityType not found")
    return db_entity_type


@router.get("/", response_model=list[schemas.EntityType])
async def get_entity_types(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return entities.get_entity_types(db, skip=skip, limit=limit)
