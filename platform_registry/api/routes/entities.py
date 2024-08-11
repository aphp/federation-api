from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.crud import entities
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()


@router.get("/{entity_id}", response_model=schemas.Entity)
async def get_entity(entity_id: str, db: Session = Depends(database.get_db)):
    db_entity = entities.get_entity(db, entity_id=entity_id)
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity


@router.get("/", response_model=list[schemas.Entity])
async def get_entities(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return entities.get_entities(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Entity, status_code=status.HTTP_201_CREATED)
async def create_entity(entity: schemas.EntityCreate, db: Session = Depends(database.get_db)):
    return entities.create_entity(db=db, entity=entity)


@router.post("/types", response_model=schemas.EntityType, status_code=status.HTTP_201_CREATED)
async def create_entity_type(entity_type: schemas.EntityTypeCreate, db: Session = Depends(database.get_db)):
    return entities.create_entity_type(db=db, entity_type=entity_type)


@router.get("/types/{entity_type_id}", response_model=schemas.EntityType)
async def get_entity_type(entity_type_id: str, db: Session = Depends(database.get_db)):
    db_entity_type = entities.get_entity_type(db, entity_type_id=entity_type_id)
    if db_entity_type is None:
        raise HTTPException(status_code=404, detail="EntityType not found")
    return db_entity_type


@router.get("/types", response_model=list[schemas.EntityType])
async def get_entity_types(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return entities.get_entity_types(db, skip=skip, limit=limit)
