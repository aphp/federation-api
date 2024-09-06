import uuid
from datetime import date, datetime, timedelta
from pydantic import BaseModel, EmailStr, field_serializer, AfterValidator
from typing import Optional, List, Annotated


STR_UUID = Annotated[str, AfterValidator(lambda x: str(uuid.UUID(x, version=4)))]


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
    email: Optional[EmailStr] = None
    expiration_date: Optional[datetime] = datetime.now() + timedelta(days=30)


class RegularUser(UserBase):
    id: str
    firstname: str
    lastname: str

class RegularUserCreate(UserBase):
    firstname: str
    lastname: str


class RegularUserPatch(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    expiration_date: Optional[datetime] = None


class SystemUser(UserBase):
    id: str
    role: Optional[Role] = None
    last_login: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True


class SystemUserCreate(BaseModel):
    """ represents users who can be authenticated in the system:
        i.e: Registry admins + users of type 'Platform'
    """
    role_id: STR_UUID
    hashed_password: str


class AdminUserCreateCreate(RegularUserCreate, SystemUserCreate):
    pass


class PlatformUserCreateCreate(UserBase, SystemUserCreate):
    platform_id: STR_UUID


class PlatformUser(UserBase):
    id: str
    last_login: Optional[datetime]

    class ConfigDict:
        from_attributes = True


class RegulatoryFrameworkBase(BaseModel):
    name: str
    description_url: str


class RegulatoryFrameworkCreate(RegulatoryFrameworkBase):
    pass


class RegulatoryFrameworkPatch(BaseModel):
    name: Optional[str]
    description_url: Optional[str]


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
    entity_type_id: STR_UUID


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
    code: Optional[str] = ""
    name: Optional[str] = ""
    framework_ids: Optional[List[str]] = []


class RecipientPlatformWithPermission(BaseModel):
    platform_id: STR_UUID
    readonly: Optional[bool] = True


class ProjectShare(BaseModel):
    recipient_platform_ids: List[RecipientPlatformWithPermission]


class ProjectShareResult(BaseModel):
    success: bool


class Project(ProjectBase):
    id: str

    class ConfigDict:
        from_attributes = True


class AccessKeyBase(BaseModel):
    label: Optional[str]
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]

    @field_serializer('start_datetime')
    def serialize_start_datetime(self, start_datetime: datetime) -> str:
        return datetime.strftime(start_datetime, "%m/%d/%Y, %H:%M:%S")

    @field_serializer('end_datetime')
    def serialize_end_datetime(self, end_datetime: datetime) -> str:
        return datetime.strftime(end_datetime, "%m/%d/%Y, %H:%M:%S")


class AccessKeyCreate(BaseModel):
    platform_id: STR_UUID


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


class PlatformPatch(PlatformBase):
    pass


class PlatformRecipient(PlatformBase):
    id: str


class Platform(PlatformBase):
    id: str
    user_account: List[PlatformUser]
    owned_projects: Optional[List[Project]]
    shared_projects: Optional[List[Project]]
    access_keys: Optional[List[AccessKey]]

    class ConfigDict:
        from_attributes = True

    @field_serializer('user_account')
    def serialize_user_account(self, user_account: List[PlatformUser]) -> str:
        user_account = user_account and user_account[0] or None
        return user_account and f"{user_account.username}[{user_account.id}]" or "--"


class ProjectWithDetails(Project):
    owner_platform: Platform
    allowed_platforms: List[Platform]
    regulatory_frameworks: List[RegulatoryFramework]
    involved_entities: List[Entity]
    involved_users: List[RegularUser]

    @field_serializer('owner_platform')
    def serialize_owner_platform(self, owner_platform: Platform) -> str:
        return owner_platform.name

    @field_serializer('allowed_platforms')
    def serialize_allowed_platforms(self, allowed_platforms: List[Platform]) -> List[str]:
        return [p.name for p in allowed_platforms]


class LoginResponse(BaseModel):
    access_token: str
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    last_login: Optional[datetime]
    role: Optional[str] = None
    is_admin: bool

    @field_serializer('last_login')
    def serialize_last_login(self, last_login: datetime) -> str:
        return datetime.strftime(last_login, "%m/%d/%Y, %H:%M")
