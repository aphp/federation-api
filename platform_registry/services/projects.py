from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import or_, and_

from platform_registry.models import User, Project, PlatformsSharedProjectsRel
from platform_registry.schemas import ProjectCreate, ProjectPatch, ProjectShare, ProjectShareResult
from platform_registry.services import regulatory_frameworks, users, entities


def get_projects(db: Session, user: User):
    projects_filter = []
    if user.role.is_platform:
        projects_filter.append(or_(Project.owner_platform_id == user.platform_id,
                                   Project.id in (proj.id for proj in user.platform.shared_projects)
                                   ))
    return db.query(Project).filter(*projects_filter).all()


def get_project_by_id(db: Session, project_id: str):
    return db.query(Project).filter(Project.id == project_id).first()


def build_objects(db, project_data) -> None:
    framework_ids = project_data.pop("framework_ids", None)
    if framework_ids:
        project_data["regulatory_frameworks"] = regulatory_frameworks.get_regulatory_frameworks(db=db, ids=framework_ids)
    user_ids = project_data.pop("user_ids", None)
    if user_ids:
        project_data["involved_users"] = users.get_regular_users(db=db, ids=user_ids)
    entity_ids = project_data.pop("entity_ids", None)
    if entity_ids:
        project_data["involved_entities"] = entities.get_entities(db=db, ids=entity_ids)


def create_project(db: Session, project: ProjectCreate, platform_id: str):
    project_data = project.model_dump(exclude_unset=True)
    build_objects(db=db, project_data=project_data)
    new_project = Project(**project_data, owner_platform_id=platform_id)
    db.add(new_project)
    db.commit()
    return new_project


def update_project(db: Session, project: Project, project_in: ProjectPatch):
    project_data = project_in.model_dump(exclude_unset=True)
    build_objects(db, project_data)
    for key, value in project_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def share_project(db: Session, project: Project, share_with: ProjectShare):
    for recipient in share_with.recipient_platform_ids:
        if recipient.platform_id != project.owner_platform_id:
            shared_project = PlatformsSharedProjectsRel(project_id=project.id,
                                                        **recipient.model_dump())
            db.add(shared_project)
            db.commit()
            db.refresh(shared_project)
    return ProjectShareResult(success=True)


def platform_can_access_project(platform, target_project) -> bool:
    return target_project.owner_platform_id == platform.id or \
           target_project.id in [p.id for p in platform.shared_projects]


def platform_can_edit_project(db: Session, platform, target_project) -> bool:
    shared_projects_rels = db.query(PlatformsSharedProjectsRel)\
                             .filter(and_(and_(PlatformsSharedProjectsRel.project_id == target_project.id,
                                               PlatformsSharedProjectsRel.platform_id == platform.id),
                                          not PlatformsSharedProjectsRel.readonly))\
                             .all()
    writable_projects = [rel.project_id for rel in shared_projects_rels]
    return platform.id == target_project.owner_platform_id or target_project.id in writable_projects

def platform_can_share_project(platform, project) -> bool:
    return project.owner_platform_id == platform.id
