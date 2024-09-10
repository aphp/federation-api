from typing import List

from sqlalchemy.orm import Session

from platform_registry.models import EntityType, Entity
from platform_registry.schemas import EntityTypeCreate, EntityCreate


def get_entity_type(db: Session, entity_type_id: str):
    return db.query(EntityType).filter(EntityType.id == entity_type_id).first()


def create_entity_type(db: Session, entity_type: EntityTypeCreate):
    db_entity_type = EntityType(name=entity_type.name)
    db.add(db_entity_type)
    db.commit()
    db.refresh(db_entity_type)
    return db_entity_type


def get_entity_types(db: Session):
    return db.query(EntityType).all()


def get_entity(db: Session, entity_id: str):
    return db.query(Entity).filter(Entity.id == entity_id).first()


def create_entity(db: Session, entity: EntityCreate):
    db_entity = Entity(
        name=entity.name,
        entity_type_id=entity.entity_type_id
    )
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def get_entities(db: Session, ids: List[str] = None):
    entities_filter = []
    if ids:
        entities_filter.append(Entity.id.in_(ids))
    return db.query(Entity).filter(*entities_filter).all()
