from datetime import date
from pydantic import BaseModel
from typing import Optional


class ProjectBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: str

    class ConfigDict:
        from_attributes = True
