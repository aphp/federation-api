from uuid import uuid4

from sqlalchemy import Column, String, ForeignKey, DateTime, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


# todo: check relations between tables          /!\

Base = declarative_base()


user_roles = Table('user_roles',
                   Base.metadata,
                   Column('user_id', UUID, ForeignKey('user.id'), primary_key=True),
                   Column('role_id', UUID, ForeignKey('role.id'), primary_key=True))


class CommonColumnsMixin(object):
    id = Column(UUID(as_uuid=False), default=uuid4, primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    modified_at = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())


class User(CommonColumnsMixin, Base):
    __tablename__ = "user"

    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    expiration_date = Column(DateTime, nullable=True)
    hashed_password = Column(String, nullable=True)
    roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(CommonColumnsMixin, Base):
    __tablename__ = "role"
    name = Column(String, unique=True, index=True)
    users = relationship("User", secondary=user_roles, back_populates="roles")


class RegulatoryFramework(CommonColumnsMixin, Base):
    __tablename__ = "regulatory_framework"

    name = Column(String, index=True)
    description_url = Column(String)


class EntityType(CommonColumnsMixin, Base):
    __tablename__ = "entity_type"

    name = Column(String, index=True)


class Entity(CommonColumnsMixin, Base):
    __tablename__ = "entity"

    name = Column(String, index=True)
    entity_type_id = Column(UUID, ForeignKey("entity_type.id"))


class ProjectMembership(CommonColumnsMixin, Base):
    __tablename__ = "project_membership"

    entity_id = Column(UUID, ForeignKey("entity.id"), nullable=False)
    project_id = Column(UUID, ForeignKey("project.id"), nullable=False, index=True)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False, index=True)
    functional_role = Column(String)


class ProjectRegulatoryFramework(CommonColumnsMixin, Base):
    __tablename__ = "project_regulatory_framework"

    project_id = Column(UUID, ForeignKey("project.id"), nullable=False, index=True)
    regulatory_framework_id = Column(UUID, ForeignKey("regulatory_framework.id"), nullable=False, index=True)


class Platform(CommonColumnsMixin, Base):
    __tablename__ = "platform"

    name = Column(String, unique=True, index=True)


class PlatformSharedProjects(CommonColumnsMixin, Base):
    __tablename__ = "platform_shared_projects"

    platform_id = Column(UUID, ForeignKey("platform.id"), nullable=False, index=True)
    project_id = Column(UUID, ForeignKey("project.id"), nullable=False, index=True)


class Project(CommonColumnsMixin, Base):
    __tablename__ = "project"

    code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
