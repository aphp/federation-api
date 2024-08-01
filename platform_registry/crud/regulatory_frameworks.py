from sqlalchemy.orm import Session

from platform_registry import models, schemas


def get_regulatory_frameworks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.RegulatoryFramework).offset(skip).limit(limit).all()


def get_regulatory_framework(db: Session, framework_id: str):
    return db.query(models.RegulatoryFramework).filter(models.RegulatoryFramework.id == framework_id).first()


def create_regulatory_framework(db: Session, regulatory_framework: schemas.RegulatoryFrameworkCreate):
    db_regulatory_framework = models.RegulatoryFramework(**regulatory_framework.model_dump())
    db.add(db_regulatory_framework)
    db.commit()
    db.refresh(db_regulatory_framework)
    return db_regulatory_framework


def update_regulatory_framework(db: Session,
                                framework: models.RegulatoryFramework,
                                framework_in: schemas.RegulatoryFrameworkPatch):
    framework_data = framework_in.model_dump()
    for key, value in framework_data.items():
        setattr(framework, key, value)
    db.commit()
    db.refresh(framework)
    return framework
