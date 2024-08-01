from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    is_registry_admin: bool
    is_platform: bool


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
