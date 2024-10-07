import datetime

from sqlalchemy import Integer, Sequence, ForeignKey, String, Uuid
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase, mapped_column, Mapped, relationship
from typing_extensions import Annotated

__all__ = ()


class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""


# serial_pk = Annotated[int, mapped_column(Integer, Sequence("id_seq"), primary_key=True)]
uuid = Annotated[str, mapped_column(Uuid)]
uuid_pk = Annotated[str, mapped_column(Uuid, primary_key=True)]
user_fk = Annotated[int, mapped_column(ForeignKey("users.id"))]


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)


class TodoListModel(Base):
    __tablename__ = "todo_list"

    id: Mapped[uuid_pk]
    user_id: Mapped[user_fk]
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    tasks = relationship("TaskModel", order_by="TaskModel.id.desc()", backref="todo_list")


class TaskModel(Base):
    __tablename__ = "task"

    id: Mapped[uuid_pk]
    todo_list_id: Mapped[uuid] = mapped_column(ForeignKey("todo_list.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(index=True, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(index=True, nullable=False)
    datetime_to_do: Mapped[datetime.datetime] = mapped_column(index=True, nullable=False)
    task_info: Mapped[str] = mapped_column(nullable=False)
