from typing import List

from sqlalchemy.orm import Session

from platform_registry.models import RegulatoryFramework
from platform_registry.schemas import RegulatoryFrameworkCreate, RegulatoryFrameworkPatch


def get_regulatory_frameworks(db: Session, ids: List[str] = None):
    frameworks_filter = []
    if ids:
        frameworks_filter.append(RegulatoryFramework.id.in_(ids))
    return db.query(RegulatoryFramework).filter(*frameworks_filter).all()


def get_regulatory_framework(db: Session, framework_id: str):
    return db.query(RegulatoryFramework).filter(RegulatoryFramework.id == framework_id).first()


def create_regulatory_framework(db: Session, regulatory_framework: RegulatoryFrameworkCreate):
    db_regulatory_framework = RegulatoryFramework(**regulatory_framework.model_dump())
    db.add(db_regulatory_framework)
    db.commit()
    db.refresh(db_regulatory_framework)
    return db_regulatory_framework


def update_regulatory_framework(db: Session,
                                framework: RegulatoryFramework,
                                framework_in: RegulatoryFrameworkPatch):
    framework_data = framework_in.model_dump()
    for key, value in framework_data.items():
        setattr(framework, key, value)
    db.commit()
    db.refresh(framework)
    return framework
