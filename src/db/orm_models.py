# NOT USED! this is the imperative implementation of the ORM models,
# which isn't used anywhere in the project because mappers break pydantic models

from sqlalchemy import Table, Column, Integer, Sequence, ForeignKey, DateTime, Text, Uuid, String
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import registry

from src.domain import model


mapper_registry = registry()
metadata = mapper_registry.metadata

users = Table(
    "users",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("username", String(50), nullable=False),
    Column("password", BYTEA, nullable=False),
)

todo_lists = Table(
    "todo_lists",
    metadata,
    Column("id", Uuid, Sequence("todo_list_id_seq"), primary_key=True),
    Column("user_id", Uuid, ForeignKey("users.id"), nullable=True),
    Column("version_number", Integer, nullable=False)
)

tasks = Table(
    "tasks",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("todo_list_id", Uuid, ForeignKey("todo_lists.id"), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    Column("datetime_to_do", DateTime, nullable=False),
    Column("info", Text, nullable=False)
)


mapper = mapper_registry.map_imperatively

def start_mappers():
    tasks_mapper = mapper(model.Task, tasks)
    mapper(
        model.TodoList,
        todo_lists,
        properties={
            "tasks": relationship(
                tasks_mapper,
                collection_class=list,
                backref=backref("todo_list", uselist=False, lazy="selectin")
            )
        }
    )
    mapper(model.User, users)
    # print(model.User(username="1", password=b"2"))
