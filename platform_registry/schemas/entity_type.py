from pydantic import BaseModel


class EntityTypeBase(BaseModel):
    name: str


class EntityTypeCreate(EntityTypeBase):
    pass


class EntityType(EntityTypeBase):
    id: str

    class ConfigDict:
        from_attributes = True
        