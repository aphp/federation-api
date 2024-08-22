from sqlalchemy.orm import Session

from platform_registry.crud.regulatory_frameworks import get_regulatory_framework
from platform_registry.models import Project, ProjectsRegulatoryFrameworksRel, PlatformsSharedProjectsRel
from platform_registry.schemas import User, ProjectCreate, ProjectPatch, ProjectShare


def get_projects(db: Session, projects_reader: User):
    projects_filter = []
    if projects_reader.role.is_platform:
        projects_filter.append(Project.owner_platform_id == projects_reader.platform_id)
    return db.query(Project).filter(*projects_filter).all()


def get_project(db: Session, project_id: str):
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, project: ProjectCreate, user):
    new_project = Project(**project.model_dump(exclude={"framework_ids"}),
                          owner_platform_id=user.platform_id)
    db.add(new_project)
    db.commit()
    for framework_id in project.framework_ids:
        framework = get_regulatory_framework(db, framework_id=framework_id)
        proj_framework = ProjectsRegulatoryFrameworksRel(project_id=new_project.id,
                                                         regulatory_framework_id=framework.id)
        db.add(proj_framework)
        db.commit()
    db.refresh(new_project)
    return new_project


def update_project(db: Session, project: Project, project_in: ProjectPatch):
    project_data = project_in.model_dump()
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
