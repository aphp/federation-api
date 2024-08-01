from sqlalchemy.orm import Session

from platform_registry import models, schemas


def get_entity_type(db: Session, entity_type_id: str):
    return db.query(models.EntityType).filter(models.EntityType.id == entity_type_id).first()


def create_entity_type(db: Session, entity_type: schemas.EntityTypeCreate):
    db_entity_type = models.EntityType(name=entity_type.name)
    db.add(db_entity_type)
    db.commit()
    db.refresh(db_entity_type)
    return db_entity_type


def get_entity_types(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.EntityType).offset(skip).limit(limit).all()


def get_entity(db: Session, entity_id: str):
    return db.query(models.Entity).filter(models.Entity.id == entity_id).first()


def create_entity(db: Session, entity: schemas.EntityCreate):
    db_entity = models.Entity(
        name=entity.name,
        entity_type_id=entity.entity_type_id
    )
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def get_entities(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Entity).offset(skip).limit(limit).all()
