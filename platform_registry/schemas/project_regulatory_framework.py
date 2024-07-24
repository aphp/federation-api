from pydantic import BaseModel


class ProjectRegulatoryFrameworkBase(BaseModel):
    project_id: str
    regulatory_framework_id: str


class ProjectRegulatoryFrameworkCreate(ProjectRegulatoryFrameworkBase):
    pass


class ProjectRegulatoryFramework(ProjectRegulatoryFrameworkBase):
    class ConfigDict:
        from_attributes = True
