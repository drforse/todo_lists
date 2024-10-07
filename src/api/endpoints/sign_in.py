from fastapi import APIRouter, Form
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.api import auth
from src.api.auth import authenticate_user, AuthenticationError
from src.api.schemas.error import ErrorResponse
from src.api.schemas.jwt import JWTSchema
from src.api.schemas.success import SuccessResponse
from src.db.unit_of_work import UnitOfWork


JWTResponse = SuccessResponse[JWTSchema]

class EmailOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(self, username: str = Form(), password: str = Form()):
        super().__init__(username=username, password=password)

router = APIRouter()

@router.post(
    "/sign-in",
    status_code=200,
    response_model=JWTResponse,
    tags=["auth"],
)
async def sign_in(
        credentials: EmailOAuth2PasswordRequestForm = Depends(),
):
    try:
        user = await authenticate_user(credentials.username, credentials.password, UnitOfWork())
    except AuthenticationError as e:
        return ErrorResponse(message=e.message).json_response(status.HTTP_401_UNAUTHORIZED)

    tokens = auth.generate_tokens(user.id)

    return JWTResponse(result=tokens)
