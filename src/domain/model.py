import datetime
import uuid

from dataclasses import dataclass, field

from src.utils.datetime_utils import utcnow


@dataclass
class User:
    username: str
    password: bytes
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    # def copy(self):
    #     return User(username=self.username, password=self.password, id=self.id)


@dataclass
class TodoList:
    user_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    version_number: int = 0

    tasks: list['Task'] = field(default_factory=list)

    def add_task(self, task: 'Task'):
        self.tasks.append(task)


@dataclass
class Task:
    datetime_to_do: datetime.datetime
    info: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime.datetime = field(default_factory=utcnow)
    updated_at: datetime.datetime = field(default_factory=utcnow)

    todo_list: TodoList | None = None
