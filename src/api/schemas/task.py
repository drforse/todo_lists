import datetime
import uuid

from src.api.schemas.base import BaseSchema


class TaskSchema(BaseSchema):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    datetime_to_do: datetime.datetime
    info: str
