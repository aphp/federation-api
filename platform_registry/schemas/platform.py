from typing import List

from pydantic import BaseModel

from platform_registry.schemas import Project


class PlatformBase(BaseModel):
    name: str


class PlatformCreate(PlatformBase):
    pass


class Platform(PlatformBase):
    id: str
    shared_projects: List[Project]

    class ConfigDict:
        from_attributes = True
