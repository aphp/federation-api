from pydantic import BaseModel


class ProjectMembershipBase(BaseModel):
    entity_id: str
    project_id: str
    user_id: str
    functional_role: str


class ProjectMembershipCreate(ProjectMembershipBase):
    pass


class ProjectMembership(ProjectMembershipBase):
    id: str

    class ConfigDict:
        from_attributes = True
