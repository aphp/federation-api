from pydantic import BaseModel


class PlatformSharedProjectsBase(BaseModel):
    platform_id: str
    project_id: str


class PlatformSharedProjectsCreate(PlatformSharedProjectsBase):
    pass


class PlatformSharedProjects(PlatformSharedProjectsBase):
    class ConfigDict:
        from_attributes = True
