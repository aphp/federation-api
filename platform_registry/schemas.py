from datetime import date, datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class RoleBase(BaseModel):
    name: str
    is_registry_admin: bool
    is_platform: bool


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: str
    manage_users: bool
    manage_roles: bool
    manage_platforms: bool
    manage_access_keys: bool
    manage_regulatory_frameworks: bool
    manage_projects: bool
    manage_projects_membership: bool
    manage_entities: bool

    class ConfigDict:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    expiration_date: Optional[datetime] = datetime.now() + timedelta(days=30)


class UserCreate(UserBase):
    password: str
    role_id: Optional[str] = None
    platform_id: Optional[str] = None


class User(UserBase):
    id: str
    role: Optional[Role] = None

    class ConfigDict:
        from_attributes = True


class RegulatoryFrameworkBase(BaseModel):
    name: str
    description_url: str


class RegulatoryFrameworkCreate(RegulatoryFrameworkBase):
    pass


class RegulatoryFrameworkPatch(RegulatoryFrameworkBase):
    pass


class RegulatoryFramework(RegulatoryFrameworkBase):
    id: str

    class ConfigDict:
        from_attributes = True


class EntityTypeBase(BaseModel):
    name: str


class EntityTypeCreate(EntityTypeBase):
    pass


class EntityType(EntityTypeBase):
    id: str

    class ConfigDict:
        from_attributes = True


class EntityBase(BaseModel):
    name: str


class EntityCreate(EntityBase):
    entity_type_id: str


class Entity(EntityBase):
    id: str
    entity_type: EntityType

    class ConfigDict:
        from_attributes = True


class ProjectBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    owner_platform_id: str


class ProjectPatch(ProjectBase):
    pass


class Project(ProjectBase):
    id: str

    class ConfigDict:
        from_attributes = True


class PlatformBase(BaseModel):
    name: str


class PlatformCreate(PlatformBase):
    pass


class Platform(PlatformBase):
    id: str
    shared_projects: List[Project]

    class ConfigDict:
        from_attributes = True


class ProjectWithDetails(Project):
    regulatory_frameworks: List[RegulatoryFramework]
    entities_involved: List[Entity]
    users_involved: List[User]
    allowed_platforms: List[Platform]


class AccessKeyBase(BaseModel):
    name: str
    start_datetime: datetime
    end_datetime: datetime


class AccessKeyCreate(AccessKeyBase):
    platform_id: str


class AccessKeyPatch(AccessKeyBase):
    pass


class AccessKey(AccessKeyBase):
    id: str
    key: str
    platform: Platform

    class ConfigDict:
        from_attributes = True
