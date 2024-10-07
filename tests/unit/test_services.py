import uuid

import pytest

from src.db import unit_of_work
from src.db.repositories.todo_lists import AbstractTodoListsRepository
from src.db.repositories.users import AbstractUsersRepository
from src.domain import model
from src.service_layer.services import users
from src.service_layer.services.todo_lists import add_task_to_first_user_todo_list, update_task_if_owned_by_user, \
    TaskNotOwnedByUserError, TaskNotFoundError
from src.utils.datetime_utils import utcnow


class FakeTodoListsRepository(AbstractTodoListsRepository):
    def __init__(self, todo_lists: list):
        self._todo_lists = todo_lists

    async def get_by_id(self, id_):
        for todo_list in self._todo_lists:
            if todo_list.id == id_:
                return todo_list

    async def get_by_user_id(self, user_id):
        for todo_list in self._todo_lists:
            if todo_list.user_id == user_id:
                return todo_list

    async def get_task_by_id(self, task_id: uuid.UUID):
        for todo_list in self._todo_lists:
            for task in todo_list.tasks:
                if task.id == task_id:
                    task.todo_list = todo_list
                    return task

    def add(self, todo_list: model.TodoList):
        self._todo_lists.append(todo_list)


class FakeUsersRepository(AbstractUsersRepository):
    def __init__(self, users: list):
        self._users = users

    async def get_by_id(self, id_: uuid.UUID):
        for user in self._users:
            if user.id == id_:
                return user

    async def get_by_username(self, username):
        for user in self._users:
            if user.username == username:
                return user

    def add(self, user):
        self._users.append(user)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.todo_lists = FakeTodoListsRepository([])
        self.users = FakeUsersRepository([])
        self.committed = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass



@pytest.mark.anyio
async def test_add_task_to_new_todo_list():
    user_id = uuid.uuid4()
    uow = FakeUnitOfWork()
    await add_task_to_first_user_todo_list(user_id, utcnow(), "test task", uow)
    assert await uow.todo_lists.get_by_user_id(user_id) is not None
    assert uow.committed


@pytest.mark.anyio
async def test_add_task_to_existing_todo_list():
    user_id = uuid.uuid4()
    uow = FakeUnitOfWork()
    await add_task_to_first_user_todo_list(user_id, utcnow(), "test task", uow)
    await add_task_to_first_user_todo_list(user_id, utcnow(), "test task 1", uow)
    assert len((await uow.todo_lists.get_by_user_id(user_id)).tasks) == 2
    assert len(uow.todo_lists._todo_lists) == 1
    assert uow.committed


@pytest.mark.anyio
async def test_update_task_owned_by_user():
    user_id = uuid.uuid4()
    uow = FakeUnitOfWork()
    await add_task_to_first_user_todo_list(user_id, utcnow(), "test task", uow)
    task = (await uow.todo_lists.get_by_user_id(user_id)).tasks[0]
    await update_task_if_owned_by_user(task.id, user_id, utcnow(), "updated task", uow)
    assert (await uow.todo_lists.get_task_by_id(task.id)).info == "updated task"
    assert uow.committed


@pytest.mark.anyio
async def test_update_task_not_owned_by_user():
    user_id = uuid.uuid4()
    uow = FakeUnitOfWork()
    await add_task_to_first_user_todo_list(user_id, utcnow(), "test task", uow)
    task = (await uow.todo_lists.get_by_user_id(user_id)).tasks[0]
    with pytest.raises(TaskNotOwnedByUserError) as exc_info:
        await update_task_if_owned_by_user(task.id, uuid.uuid4(), utcnow(), "updated task", uow)
    assert isinstance(exc_info.value, TaskNotOwnedByUserError)


@pytest.mark.anyio
async def test_update_task_not_found():
    user_id = uuid.uuid4()
    uow = FakeUnitOfWork()
    await add_task_to_first_user_todo_list(user_id, utcnow(), "test task", uow)
    task = (await uow.todo_lists.get_by_user_id(user_id)).tasks[0]
    with pytest.raises(TaskNotFoundError) as exc_info:
        await update_task_if_owned_by_user(uuid.uuid4(), user_id, utcnow(), "updated task", uow)
    assert isinstance(exc_info.value, TaskNotFoundError)


@pytest.mark.anyio
async def test_add_user():
    uow = FakeUnitOfWork()
    user_id = await users.add("test", b"test", uow)
    assert isinstance(user_id, uuid.UUID)
    assert await uow.users.get_by_id(user_id) is not None
    assert uow.committed


@pytest.mark.anyio
async def test_add_user_already_exists():
    uow = FakeUnitOfWork()
    await users.add("test", b"test", uow)
    with pytest.raises(users.UserAlreadyExistsError) as exc_info:
        await users.add("test", b"test", uow)
    assert isinstance(exc_info.value, users.UserAlreadyExistsError)
