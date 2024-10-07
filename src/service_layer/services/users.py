import uuid

from src.db.unit_of_work import AbstractUnitOfWork
from src.domain import model


class UserAlreadyExistsError(Exception):
    pass


async def add(username: str, password: bytes, uow: AbstractUnitOfWork) -> uuid.UUID:
    """add a new user to the database, return the user's id"""
    async with uow:
        user = await uow.users.get_by_username(username)
        if user:
            raise UserAlreadyExistsError(f"User {user.username} already exists")
        user = model.User(username=username, password=password)
        uow.users.add(user)
        await uow.commit()
        # print(f"{user=}")
        return user.id
