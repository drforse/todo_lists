import datetime
import decimal
from typing import Literal, Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class SuccessResponse(GenericModel, Generic[T]):
    success: Literal[True] = True
    result: T | None = None

    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.timestamp(),
            decimal.Decimal: str
        }
