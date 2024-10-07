import abc
import uuid

from sqlalchemy.sql import select

from src.domain import model


class AbstractUsersRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, id_: uuid.UUID):
        pass

    @abc.abstractmethod
    async def get_by_username(self, username: str):
        pass

    @abc.abstractmethod
    def add(self, user: model.User):
        pass


class UsersRepository(AbstractUsersRepository):
    def __init__(self, session):
        self.session = session

    async def get_by_id(self, id_: uuid.UUID) -> model.User | None:
        return await self.session.get(model.User, id_)

    async def get_by_username(self, username: str) -> model.User | None:
        query = select(model.User).filter_by(username=username)
        return await self.session.scalar(query)

    def add(self, user: model.User):
        self.session.add(user)
