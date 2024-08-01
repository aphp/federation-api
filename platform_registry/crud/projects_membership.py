from sqlalchemy.orm import Session

from platform_registry import models, schemas


def get_project_membership(db: Session, project_membership_id: str):
    return db.query(models.ProjectMembership).filter(models.ProjectMembership.id == project_membership_id).first()


def create_project_membership(db: Session, project_membership: schemas.ProjectMembershipCreate):
    db_project_membership = models.ProjectMembership(
        entity_id=project_membership.entity_id,
        project_id=project_membership.project_id,
        user_id=project_membership.user_id,
        functional_role=project_membership.functional_role
    )
    db.add(db_project_membership)
    db.commit()
    db.refresh(db_project_membership)
    return db_project_membership


def get_project_memberships(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ProjectMembership).offset(skip).limit(limit).all()
