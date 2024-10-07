from typing import Any
from uuid import UUID

from sqlalchemy import text

from src.db.unit_of_work import UnitOfWork


async def get_tasks_list_by_user_id(user_id: UUID, uow: UnitOfWork) -> list[dict[str, Any]]:
    async with uow:
        result = await uow.session.execute(
            text("SELECT * FROM tasks WHERE (SELECT user_id FROM todo_lists WHERE id = todo_list_id) = :user_id"),
            {"user_id": user_id}
        )
        return [{"id": row.id,
                 "created_at": row.created_at,
                 "updated_at": row.updated_at,
                 "datetime_to_do": row.datetime_to_do,
                 "info": row.info} for row in result]


async def get_task_with_owner_id(task_id: UUID, uow: UnitOfWork) -> dict[str, Any] | None:
    async with uow:
        result = await uow.session.execute(
            text("SELECT tasks.*, users.id FROM tasks "
                 "JOIN todo_lists ON tasks.todo_list_id = todo_lists.id "
                 "JOIN users ON todo_lists.user_id = users.id "
                 "WHERE tasks.id = :task_id"),
            {"task_id": task_id}
        )
        row = result.fetchone()
        if row is None:
            return None
        return {"id": row.id,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "datetime_to_do": row.datetime_to_do,
                "info": row.info,
                "owner_id": row[-1]}
