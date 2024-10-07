import uuid
from typing import Any

from sqlalchemy import text

from src.db.unit_of_work import UnitOfWork


async def get_by_id(id_: uuid.UUID, uow: UnitOfWork) -> dict[str, Any] | None:
    async with uow:
        result = await uow.session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": id_})
        user = result.fetchone()
        return {"id": user.id, "username": user.username, "password": user.password} if user else None


async def get_by_username(username: str, uow: UnitOfWork) -> dict[str, Any] | None:
    async with uow:
        result = await uow.session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        )
        user = result.fetchone()
        return {"id": user.id, "username": user.username, "password": user.password} if user else None
