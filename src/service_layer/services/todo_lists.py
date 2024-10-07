import datetime
import uuid

from src.db.unit_of_work import AbstractUnitOfWork
from src.domain import model
from src.utils.datetime_utils import utcnow


class TaskNotOwnedByUserError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


async def add_task_to_first_user_todo_list(
    user_id: uuid.UUID,
    datetime_to_do: datetime.datetime,
    task_info: str,
    uow: AbstractUnitOfWork,
) -> None:
    async with uow:
        todo_list = await uow.todo_lists.get_by_user_id(user_id)
        if todo_list is None:
            todo_list = model.TodoList(user_id=user_id)
            uow.todo_lists.add(todo_list)
        todo_list.tasks.append(model.Task(datetime_to_do=datetime_to_do, info=task_info))

        await uow.commit()


async def update_task_if_owned_by_user(
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    datetime_to_do: datetime.datetime | None,
    task_info: str | None,
    uow: AbstractUnitOfWork,
) -> None:
    """

    :param task_id:
    :param user_id:
    :param datetime_to_do: if none then it will not be updated
    :param task_info: if none then it will not be updated
    :param uow:
    :return:
    """
    async with uow:
        task = await uow.todo_lists.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with id {task_id} not found.")
        if task.todo_list.user_id != user_id:
            raise TaskNotOwnedByUserError(f"Task with id {task_id} is not owned by user with id {user_id}.")
        if datetime_to_do is not None:
            task.datetime_to_do = datetime_to_do
        if task_info is not None:
            task.info = task_info
        task.updated_at = utcnow()
        await uow.commit()
