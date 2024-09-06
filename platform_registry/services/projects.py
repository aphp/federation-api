from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import or_, and_

from platform_registry.models import User, Project, ProjectsRegulatoryFrameworksRel, PlatformsSharedProjectsRel
from platform_registry.schemas import ProjectCreate, ProjectPatch, ProjectShare, ProjectShareResult


def get_projects(db: Session, user: User):
    projects_filter = []
    if user.role.is_platform:
        projects_filter.append(or_(Project.owner_platform_id == user.platform_id,
                                   Project.id in (proj.id for proj in user.platform.shared_projects)
                                   ))
    return db.query(Project).filter(*projects_filter).all()


def get_project_by_id(db: Session, project_id: str):
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, project: ProjectCreate, platform_id: str):
    new_project = Project(**project.model_dump(exclude={"framework_ids"}),
                          owner_platform_id=platform_id)
    db.add(new_project)
    db.commit()
    for framework_id in project.framework_ids:
        proj_framework = ProjectsRegulatoryFrameworksRel(project_id=new_project.id,
                                                         regulatory_framework_id=framework_id)
        db.add(proj_framework)
    db.commit()
    db.refresh(new_project)
    return new_project


def update_project(db: Session, project: Project, project_in: ProjectPatch):
    project_data = project_in.model_dump(exclude={"framework_ids"})
    for key, value in project_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)

    actual_framework_ids = [f.id for f in project.regulatory_frameworks]
    new_framework_ids = [fid for fid in project_in.framework_ids if fid not in actual_framework_ids]
    removable_framework_ids = [fid for fid in actual_framework_ids if fid not in project_in.framework_ids]

    proj_frm_to_remove = db.query(ProjectsRegulatoryFrameworksRel)\
                           .filter(and_(ProjectsRegulatoryFrameworksRel.project_id == project.id,
                                        ProjectsRegulatoryFrameworksRel.regulatory_framework_id.in_(removable_framework_ids)))\
                           .all()
    for pf in proj_frm_to_remove:
        db.delete(pf)

    for f_id in new_framework_ids:
        proj_frm = ProjectsRegulatoryFrameworksRel(project_id=project.id,
                                                   regulatory_framework_id=f_id)
        db.add(proj_frm)
        db.commit()

    db.commit()
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
                                          PlatformsSharedProjectsRel.readonly))\
                             .all()
    writable_projects = [rel.project_id for rel in shared_projects_rels]
    return platform.id == target_project.owner_platform_id or target_project.id in writable_projects

def platform_can_share_project(platform, project) -> bool:
    return project.owner_platform_id == platform.id
