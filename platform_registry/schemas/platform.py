from pydantic import BaseModel


class PlatformBase(BaseModel):
    name: str


class PlatformCreate(PlatformBase):
    pass


class Platform(PlatformBase):
    id: str

    class ConfigDict:
        from_attributes = True
