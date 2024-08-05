from fastapi import APIRouter, Depends, HTTPException
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


@router.post("/", response_model=schemas.Entity)
async def create_entity(entity: schemas.EntityCreate, db: Session = Depends(database.get_db)):
    return entities.create_entity(db=db, entity=entity)
