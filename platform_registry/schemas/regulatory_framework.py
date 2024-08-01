from pydantic import BaseModel


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
