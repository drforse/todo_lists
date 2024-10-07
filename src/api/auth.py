import uuid
from dataclasses import dataclass

from fastapi import HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from passlib.context import CryptContext
from starlette import status

from src.db.unit_of_work import UnitOfWork
from src.db.views import users as users_view
from src.utils import config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
access_security = JwtAccessBearer(secret_key=config.JWT_SECRET_KEY, auto_error=True)


class AuthenticationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@dataclass
class User:
    id: uuid.UUID
    username: str


def get_password_hash(password: str):
    return pwd_context.hash(password).encode("utf-8")


def verify_password(plain_password: str, hashed_password: bytes):
    return pwd_context.verify(plain_password, hashed_password.decode("utf-8"))


async def authenticate_user(username: str, password: str, uow: UnitOfWork) -> User:
    user = await users_view.get_by_username(username, uow)
    if not user:
        raise AuthenticationError(f"User {username} not found")
    if not verify_password(password, user["password"]):
        raise AuthenticationError("Invalid password")
    return User(id=user["id"], username=user["username"])


def generate_tokens(
        user_id: uuid.UUID,
        token_expires_delta = config.JWT_ACCESS_TOKEN_EXPIRES_DELTA,
        refresh_token_expires_delta = config.JWT_REFRESH_TOKEN_EXPIRES_DELTA
):
    token = access_security.create_access_token(
        subject={"user_id": str(user_id)},
        expires_delta=token_expires_delta,
    )
    refresh_token = access_security.create_refresh_token(
        subject={"user_id": str(user_id)},
        expires_delta=refresh_token_expires_delta,
    )
    return {"token": token, "refresh_token": refresh_token}


async def get_user(creds: JwtAuthorizationCredentials = Security(access_security)) -> User:
    print(creds["user_id"])
    user_id = uuid.UUID(creds["user_id"])

    user = await users_view.get_by_id(user_id, UnitOfWork())
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(id=user["id"], username=user["username"])
