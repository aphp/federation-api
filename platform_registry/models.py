from uuid import uuid4

from sqlalchemy import Column, String, ForeignKey, Date, DateTime, func, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class CommonColumnsMixin(object):
    id = Column(UUID(as_uuid=False), default=uuid4, primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    modified_at = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())


class User(CommonColumnsMixin, Base):
    __tablename__ = "user"

    username = Column(String, unique=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    expiration_date = Column(DateTime)
    hashed_password = Column(String)
    role_id = Column(UUID, ForeignKey("role.id"))
    platform_id = Column(UUID, ForeignKey("Platform.id"))
    role = relationship("Role", back_populates="users")
    platform = relationship("Platform", back_populates="user_account")


class Role(CommonColumnsMixin, Base):
    __tablename__ = "role"

    name = Column(String, unique=True, index=True)
    is_registry_admin = Column(Boolean, nullable=False)
    is_platform = Column(Boolean, nullable=False)
    manage_users = Column(Boolean, nullable=False)
    manage_roles = Column(Boolean, nullable=False)
    manage_platforms = Column(Boolean, nullable=False)
    manage_access_keys = Column(Boolean, nullable=False)
    manage_regulatory_frameworks = Column(Boolean, nullable=False)
    manage_projects = Column(Boolean, nullable=False)
    manage_projects_membership = Column(Boolean, nullable=False)
    manage_entities = Column(Boolean, nullable=False)
    users = relationship("User", back_populates="role")
    __table_args__ = (UniqueConstraint("name", "is_registry_admin", "is_platform",
                                       name='unique_role_config'),)


class Platform(CommonColumnsMixin, Base):
    __tablename__ = "platform"

    name = Column(String, unique=True, index=True)
    user_account = relationship("User", back_populates="platform")
    owned_projects = relationship("Project", back_populates="owner_platform")
    shared_projects = relationship("Project", secondary="platforms_shared_projects_rel", back_populates="platforms")


class EntityType(CommonColumnsMixin, Base):
    __tablename__ = "entity_type"

    name = Column(String, index=True)
    entities = relationship("Entity", back_populates="entity_type")


class Entity(CommonColumnsMixin, Base):
    __tablename__ = "entity"

    name = Column(String, index=True)
    entity_type_id = Column(UUID, ForeignKey("entity_type.id"))
    entity_type = relationship("EntityType", back_populates="entities")


class Project(CommonColumnsMixin, Base):
    __tablename__ = "project"

    code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    owner_platform_id = Column(UUID, ForeignKey("platform.id"))
    owner_platform = relationship("Platform", back_populates="owned_projects")
    regulatory_frameworks = relationship("RegulatoryFramework", secondary="projects_regulatory_frameworks_rel", back_populates="projects")
    platforms = relationship("Platform", secondary="platforms_shared_projects_rel", back_populates="shared_projects")


class RegulatoryFramework(CommonColumnsMixin, Base):
    __tablename__ = "regulatory_framework"

    name = Column(String, index=True)
    description_url = Column(String)
    projects = relationship("Project", secondary="projects_regulatory_frameworks_rel", back_populates="regulatory_frameworks")


class ProjectsRegulatoryFrameworksRel(CommonColumnsMixin, Base):
    __tablename__ = "projects_regulatory_frameworks_rel"

    project_id = Column(UUID, ForeignKey("project.id"), nullable=False, index=True)
    regulatory_framework_id = Column(UUID, ForeignKey("regulatory_framework.id"), nullable=False, index=True)


class ProjectMembership(CommonColumnsMixin, Base):
    __tablename__ = "project_membership"

    entity_id = Column(UUID, ForeignKey("entity.id"), nullable=False)
    project_id = Column(UUID, ForeignKey("project.id"), nullable=False, index=True)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False, index=True)
    functional_role = Column(String)


class PlatformsSharedProjectsRel(CommonColumnsMixin, Base):
    __tablename__ = "platforms_shared_projects_rel"

    platform_id = Column(UUID, ForeignKey("platform.id"), nullable=False, index=True)
    project_id = Column(UUID, ForeignKey("project.id"), nullable=False, index=True)
    read = Column(Boolean, nullable=False)
    write = Column(Boolean, nullable=False)

