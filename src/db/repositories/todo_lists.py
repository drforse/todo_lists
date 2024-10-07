import abc
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domain import model


class AbstractTodoListsRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID):
        pass

    @abc.abstractmethod
    async def get_task_by_id(self, task_id: uuid.UUID):
        pass

    @abc.abstractmethod
    def add(self, todo_list: model.TodoList):
        pass


class TodoListsRepository(AbstractTodoListsRepository):
    def __init__(self, session):
        self.session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> model.TodoList:
        query = select(model.TodoList).filter_by(user_id=user_id)
        query = query.options(selectinload(model.TodoList.tasks))
        return await self.session.scalar(query)

    async def get_task_by_id(self, task_id: uuid.UUID) -> model.Task:
        query = select(model.Task).filter_by(id=task_id)
        return await self.session.scalar(query)

    def add(self, todo_list: model.TodoList):
        self.session.add(todo_list)
