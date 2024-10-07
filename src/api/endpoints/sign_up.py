from fastapi import APIRouter, Form
from starlette import status

from src.api import auth
from src.api.schemas.error import ErrorResponse
from src.api.schemas.jwt import JWTSchema
from src.api.schemas.success import SuccessResponse
from src.db.unit_of_work import UnitOfWork
from src.service_layer.services import users


JWTResponse = SuccessResponse[JWTSchema]

router = APIRouter()

@router.post(
    "/sign-up",
    status_code=200,
    response_model=JWTResponse,
    tags=["auth"],
)
async def sign_up(
        username: str = Form(...),
        password: str = Form(...),
        repeat_password: str = Form(...),
):
    if password != repeat_password:
        return ErrorResponse(message="Passwords do not match").json_response(status.HTTP_400_BAD_REQUEST)

    user_id = await users.add(username, auth.get_password_hash(password), UnitOfWork())

    tokens = auth.generate_tokens(user_id)

    return JWTResponse(result=tokens)

