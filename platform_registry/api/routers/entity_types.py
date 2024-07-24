from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from platform_registry import crud, schemas
from platform_registry.core import database

router = APIRouter()


@router.post("/", response_model=schemas.EntityType)
async def create_entity_type(entity_type: schemas.EntityTypeCreate, db: Session = Depends(database.get_db)):
    return crud.create_entity_type(db=db, entity_type=entity_type)


@router.get("/{entity_type_id}", response_model=schemas.EntityType)
async def read_entity_type(entity_type_id: int, db: Session = Depends(database.get_db)):
    db_entity_type = crud.get_entity_type(db, entity_type_id=entity_type_id)
    if db_entity_type is None:
        raise HTTPException(status_code=404, detail="EntityType not found")
    return db_entity_type


@router.get("/", response_model=list[schemas.EntityType])
async def read_entity_types(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    entity_types = crud.get_entity_types(db, skip=skip, limit=limit)
    return entity_types
