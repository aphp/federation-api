from uuid import uuid4

from sqlalchemy import Column, String, ForeignKey, Date, DateTime, func, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class CommonColumnsMixin(object):
    id = Column(UUID(as_uuid=False), default=lambda: str(uuid4()), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    modified_at = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)


class User(CommonColumnsMixin, Base):
    __tablename__ = "user"

    username = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True, index=True)
    expiration_date = Column(DateTime)
    last_login = Column(DateTime)
    hashed_password = Column(String)
    role_id = Column(UUID(as_uuid=False), ForeignKey("role.id"), nullable=True)
    platform_id = Column(UUID(as_uuid=False), ForeignKey("platform.id"), nullable=True)
    role = relationship("Role", back_populates="users")
    platform = relationship("Platform", back_populates="user_account")
    projects = relationship("Project", secondary="project_user_rel", viewonly=True)


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
    manage_entities = Column(Boolean, nullable=False)
    users = relationship("User", back_populates="role")
    __table_args__ = (UniqueConstraint("is_registry_admin", "is_platform",
                                       name='unique_role_config'),)


class Platform(CommonColumnsMixin, Base):
    __tablename__ = "platform"

    name = Column(String, unique=True, index=True, nullable=False)
    user_account = relationship("User", back_populates="platform")
    owned_projects = relationship("Project", back_populates="owner_platform")
    shared_projects = relationship("Project", secondary="platforms_shared_projects_rel", viewonly=True)
    access_keys = relationship("AccessKey", back_populates="platform")


class Project(CommonColumnsMixin, Base):
    __tablename__ = "project"

    code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    owner_platform_id = Column(UUID(as_uuid=False), ForeignKey("platform.id"))
    owner_platform = relationship("Platform", back_populates="owned_projects")
    allowed_platforms = relationship("Platform", secondary="platforms_shared_projects_rel", viewonly=True)
    regulatory_frameworks = relationship("RegulatoryFramework", secondary="project_regulatory_framework_rel", backref="RegulatoryFramework")
    involved_entities = relationship("Entity", secondary="project_entity_rel", backref="Entity")
    involved_users = relationship("User", secondary="project_user_rel", backref="User")


class RegulatoryFramework(CommonColumnsMixin, Base):
    __tablename__ = "regulatory_framework"

    name = Column(String, index=True)
    description_url = Column(String)
    projects = relationship("Project", secondary="project_regulatory_framework_rel", viewonly=True)


class EntityType(CommonColumnsMixin, Base):
    __tablename__ = "entity_type"

    name = Column(String, index=True)
    entities = relationship("Entity", back_populates="entity_type")


class Entity(CommonColumnsMixin, Base):
    __tablename__ = "entity"

    name = Column(String, index=True, nullable=False, unique=True)
    entity_type_id = Column(UUID(as_uuid=False), ForeignKey("entity_type.id"))
    entity_type = relationship("EntityType", back_populates="entities")
    assigned_projects = relationship("Project", secondary="project_entity_rel", viewonly=True)


class AccessKey(CommonColumnsMixin, Base):
    __tablename__ = "access_key"

    label = Column(String, index=True, nullable=False, unique=True)
    key = Column(String, nullable=False, unique=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    platform_id = Column(UUID(as_uuid=False), ForeignKey("platform.id"), nullable=False)
    platform = relationship("Platform", back_populates="access_keys")


class ProjectRegulatoryFrameworkRel(CommonColumnsMixin, Base):
    __tablename__ = "project_regulatory_framework_rel"

    project_id = Column(UUID(as_uuid=False), ForeignKey("project.id"), nullable=False, index=True)
    regulatory_framework_id = Column(UUID(as_uuid=False), ForeignKey("regulatory_framework.id"), nullable=False, index=True)


class ProjectUsersRel(CommonColumnsMixin, Base):
    __tablename__ = "project_user_rel"

    project_id = Column(UUID(as_uuid=False), ForeignKey("project.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("user.id"), nullable=False, index=True)


class ProjectEntitiesRel(CommonColumnsMixin, Base):
    __tablename__ = "project_entity_rel"

    project_id = Column(UUID(as_uuid=False), ForeignKey("project.id"), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=False), ForeignKey("entity.id"), nullable=False, index=True)


class PlatformsSharedProjectsRel(CommonColumnsMixin, Base):
    __tablename__ = "platforms_shared_projects_rel"

    platform_id = Column(UUID(as_uuid=False), ForeignKey("platform.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("project.id"), nullable=False, index=True)
    readonly = Column(Boolean, nullable=False, default=True)

