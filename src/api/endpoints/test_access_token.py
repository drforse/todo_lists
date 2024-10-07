from fastapi import APIRouter, Depends

from src.api import auth
from src.api.schemas.error import ErrorResponse
from src.api.schemas.success import SuccessResponse
from src.domain import model

router = APIRouter()

@router.get(
    "/test-access-token",
    status_code=200,
    response_model=SuccessResponse[None],
    responses=ErrorResponse.responses(),
    response_model_exclude_none=True,
    tags=["tests"],
)
async def test_access_token(user: model.User = Depends(auth.get_user)):
    assert user is not None
    return SuccessResponse()