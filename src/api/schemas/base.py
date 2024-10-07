import abc

from pydantic import BaseModel as PydanticModel


class BaseSchema(abc.ABC, PydanticModel):
    class Config:
        from_attributes = True
        validate_assignment = True