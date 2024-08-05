from datetime import date
from pydantic import BaseModel
from typing import Optional, List

from platform_registry.schemas import RegulatoryFramework, Platform, Entity, User


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


class ProjectWithDetails(Project):
    regulatory_frameworks: List[RegulatoryFramework]
    entities_involved: List[Entity]
    users_involved: List[User]
    allowed_platforms: List[Platform]
