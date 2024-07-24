from pydantic import BaseModel


class EntityBase(BaseModel):
    name: str
    entity_type_id: str


class EntityCreate(EntityBase):
    pass


class Entity(EntityBase):
    id: str

    class ConfigDict:
        from_attributes = True
