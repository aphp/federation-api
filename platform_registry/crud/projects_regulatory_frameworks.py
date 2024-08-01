from sqlalchemy.orm import Session

from platform_registry import models, schemas


def get_project_regulatory_framework(db: Session, project_id: str, regulatory_framework_id: str):
    return db.query(models.ProjectsRegulatoryFrameworksRel).filter(
        models.ProjectsRegulatoryFrameworksRel.project_id == project_id,
        models.ProjectsRegulatoryFrameworksRel.regulatory_framework_id == regulatory_framework_id
    ).first()


def create_project_regulatory_framework(db: Session, project_regulatory_framework: schemas.ProjectRegulatoryFrameworkCreate):
    db_project_regulatory_framework = models.ProjectsRegulatoryFrameworksRel(
        project_id=project_regulatory_framework.project_id,
        regulatory_framework_id=project_regulatory_framework.regulatory_framework_id
    )
    db.add(db_project_regulatory_framework)
    db.commit()
    db.refresh(db_project_regulatory_framework)
    return db_project_regulatory_framework


def get_project_regulatory_frameworks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ProjectsRegulatoryFrameworksRel).offset(skip).limit(limit).all()
