from sqlalchemy import and_
from sqlalchemy.orm import Session

from platform_registry import schemas, models


def get_projects(db: Session, projects_reader: schemas.User, skip: int = 0, limit: int = 10):
    projects_filter = {}
    if projects_reader.role.is_platform:
        projects_filter = {"owner_platform_id": projects_reader.platform_id}
    return db.query(models.Project).filter(and_(**projects_filter)).offset(skip).limit(limit).all()


def get_project(db: Session, project_id: str):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def create_project(db: Session, project: schemas.ProjectCreate):
    project = models.Project(code=project.code,
                             name=project.name,
                             description=project.description,
                             start_date=project.start_date,
                             end_date=project.end_date,
                             owner_platform_id=project.owner_platform_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(*, db: Session, project: models.Project, project_in: schemas.ProjectPatch):
    project_data = project_in.model_dump()
    for key, value in project_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project
