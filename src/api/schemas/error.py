from copy import deepcopy
from typing import Literal

from starlette.responses import JSONResponse

from .base import BaseSchema

__all__ = ("ErrorResponse", )

from ...utils.schemas import form_body


@form_body
class ErrorResponse(BaseSchema):
    """Error response"""
    success: Literal[False] = False
    message: str
    validation_errors: dict[str, str] | None = None

    @classmethod
    def responses(cls, *status_codes: int) -> dict:
        no_validation_errors = deepcopy(cls.model_json_schema())
        no_validation_errors["properties"].pop("validation_errors")
        responses = {
            400: {"content": {"application/json": {"schema": cls.model_json_schema()}}},
            401: {"content": {"application/json": {"schema": no_validation_errors}}},
        }
        for status_code in status_codes:
            if status_code in responses:
                continue
            responses[status_code] = {"content": {"application/json": {"schema": no_validation_errors}}}
        return responses

    def json_response(self, status_code: int, exclude_none: bool = True) -> JSONResponse:
        return JSONResponse(self.model_dump(exclude_none=exclude_none), status_code=status_code)
