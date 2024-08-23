from datetime import date, datetime, timedelta
from pydantic import BaseModel, EmailStr, field_serializer
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
    last_login: Optional[datetime]

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
    framework_ids: List[str]


class ProjectPatch(ProjectBase):
    pass


class RecipientPlatformWithPermission(BaseModel):
    platform_id: str
    read: bool
    write: bool


class ProjectShare(BaseModel):
    recipient_platform_ids: List[RecipientPlatformWithPermission]


class Project(ProjectBase):
    id: str

    class ConfigDict:
        from_attributes = True


class AccessKeyBase(BaseModel):
    name: Optional[str]
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]

    @field_serializer('start_datetime')
    def serialize_start_datetime(self, start_datetime: datetime, _info) -> str:
        return datetime.strftime(start_datetime, "%m/%d/%Y, %H:%M:%S")

    @field_serializer('end_datetime')
    def serialize_end_datetime(self, end_datetime: datetime, _info) -> str:
        return datetime.strftime(end_datetime, "%m/%d/%Y, %H:%M:%S")


class AccessKeyCreate(BaseModel):
    platform_id: str


class AccessKeyPatch(BaseModel):
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]


class AccessKey(AccessKeyBase):
    id: str
    key: str

    class ConfigDict:
        from_attributes = True


class PlatformBase(BaseModel):
    name: str


class PlatformCreate(PlatformBase):
    pass


class Platform(PlatformBase):
    id: str
    owned_projects: Optional[List[Project]]
    shared_projects: Optional[List[Project]]
    access_keys: Optional[List[AccessKey]]

    class ConfigDict:
        from_attributes = True


class ProjectWithDetails(Project):
    owner_platform: Platform
    allowed_platforms: List[Platform]
    regulatory_frameworks: List[RegulatoryFramework]
    involved_entities: List[Entity]
    involved_users: List[User]

    @field_serializer('owner_platform')
    def serialize_owner_platform(self, owner_platform: Platform, _info) -> str:
        return owner_platform.name

    @field_serializer('allowed_platforms')
    def serialize_allowed_platforms(self, allowed_platforms: List[Platform], _info) -> List[str]:
        return [p.name for p in allowed_platforms]


class LoginResponse(BaseModel):
    access_token: str
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    last_login: Optional[datetime]
    role: Optional[str]
    is_admin: bool

    @field_serializer('last_login')
    def serialize_last_login(self, last_login: datetime, _info) -> str:
        return datetime.strftime(last_login, "%m/%d/%Y, %H:%M")
