from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.api import deps
from platform_registry.services import entities
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()
entity_types_router = APIRouter(prefix="/types")


@router.get("/", response_model=list[schemas.Entity])
async def get_entities(db: Session = Depends(database.get_db),
                       user: schemas.User = Depends(deps.either_platform_or_admin)):
    return entities.get_entities(db)


@router.get("/{entity_id}", response_model=schemas.Entity)
async def get_entity(entity_id: str,
                     db: Session = Depends(database.get_db),
                     user: schemas.User = Depends(deps.either_platform_or_admin)):
    db_entity = entities.get_entity(db, entity_id=entity_id)
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity


@router.post("/", response_model=schemas.Entity, status_code=status.HTTP_201_CREATED)
async def create_entity(entity: schemas.EntityCreate,
                        db: Session = Depends(database.get_db),
                        user: schemas.User = Depends(deps.registry_admin_user)):
    return entities.create_entity(db=db, entity=entity)


@entity_types_router.get("/", response_model=list[schemas.EntityType])
async def get_entity_types(db: Session = Depends(database.get_db),
                           user: schemas.User = Depends(deps.registry_admin_user)):
    return entities.get_entity_types(db)


@entity_types_router.get("/{entity_type_id}", response_model=schemas.EntityType)
async def get_entity_type(entity_type_id: str,
                          db: Session = Depends(database.get_db),
                          user: schemas.User = Depends(deps.registry_admin_user)):
    db_entity_type = entities.get_entity_type(db, entity_type_id=entity_type_id)
    if db_entity_type is None:
        raise HTTPException(status_code=404, detail="EntityType not found")
    return db_entity_type


@entity_types_router.post("/", response_model=schemas.EntityType, status_code=status.HTTP_201_CREATED)
async def create_entity_type(entity_type: schemas.EntityTypeCreate,
                             db: Session = Depends(database.get_db),
                             user: schemas.User = Depends(deps.registry_admin_user)):
    return entities.create_entity_type(db=db, entity_type=entity_type)


router.include_router(entity_types_router)
