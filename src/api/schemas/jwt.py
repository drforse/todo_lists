from src.api.schemas.base import BaseSchema
from src.utils.schemas import form_body


@form_body
class JWTSchema(BaseSchema):
    """JWT access token and refresh token"""
    token: str
    refresh_token: str

    @classmethod
    def content(cls):
        return {"content": {"application/json": {"schema": cls.model_json_schema()}}}
