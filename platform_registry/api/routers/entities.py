from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from platform_registry import crud, schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.Entity)
async def create_entity(entity: schemas.EntityCreate, db: Session = Depends(database.get_db)):
    return crud.create_entity(db=db, entity=entity)


@router.get("/{entity_id}", response_model=schemas.Entity)
async def read_entity(entity_id: int, db: Session = Depends(database.get_db)):
    db_entity = crud.get_entity(db, entity_id=entity_id)
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity


@router.get("/", response_model=list[schemas.Entity])
async def read_entities(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    entities = crud.get_entities(db, skip=skip, limit=limit)
    return entities
