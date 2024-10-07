import datetime
import uuid

from fastapi import APIRouter, Depends, Body, Path

from src.api import auth
from src.api.auth import User
from src.api.schemas.error import ErrorResponse
from src.api.schemas.success import SuccessResponse
from src.api.schemas.task import TaskSchema
from src.db.unit_of_work import UnitOfWork
from src.service_layer.services import todo_lists
from src.db.views import todo_lists as todo_lists_view


TasksResponse = SuccessResponse[list[TaskSchema]]
TaskResponse = SuccessResponse[TaskSchema]

router = APIRouter()

@router.post(
    "/tasks/create",
    status_code=201,
    response_model=SuccessResponse[None],
    responses=ErrorResponse.responses(),
    response_model_exclude_none=True,
    tags=["todo_list"],
)
async def create_task(
        datetime_to_do: datetime.datetime = Body(...),
        task_info: str = Body(...),
        user: User = Depends(auth.get_user)
):
    await todo_lists.add_task_to_first_user_todo_list(
        user_id=user.id,
        datetime_to_do=datetime_to_do,
        task_info=task_info,
        uow=UnitOfWork(),
    )
    return SuccessResponse()


@router.get(
    "/tasks/list",
    status_code=200,
    response_model=TasksResponse,
    responses=ErrorResponse.responses(),
    tags=["todo_list"]
)
async def get_tasks_list(user: User = Depends(auth.get_user)):
    tasks = await todo_lists_view.get_tasks_list_by_user_id(user.id, UnitOfWork())
    return TasksResponse(result=tasks)


@router.get(
    "/tasks/{task_id}",
    status_code=200,
    response_model=TaskResponse,
    responses=ErrorResponse.responses(401, 404),
    tags=["todo_list"]
)
async def get_task(
        task_id: uuid.UUID,
        user: User = Depends(auth.get_user)
):
    task = await todo_lists_view.get_task_with_owner_id(task_id, UnitOfWork())
    if task is None:
        return ErrorResponse(message="Task not found").json_response(status_code=404)
    if task["owner_id"] != user.id:
        return ErrorResponse(message="Task not owned by user").json_response(status_code=401)
    return TaskResponse(result=task)


@router.patch(
    "/tasks/{task_id}/update",
    status_code=200,
    response_model=SuccessResponse[None],
    responses=ErrorResponse.responses(401, 404),
    tags=["todo_list"]
)
async def update_task(
        task_id: uuid.UUID,
        datetime_to_do: datetime.datetime | None = Body(None),
        task_info: str | None = Body(None),
        user: User = Depends(auth.get_user)
):
    try:
        await todo_lists.update_task_if_owned_by_user(
            user_id=user.id,
            task_id=task_id,
            datetime_to_do=datetime_to_do,
            task_info=task_info,
            uow=UnitOfWork(),
        )
    except todo_lists.TaskNotFoundError:
        return ErrorResponse(message="Task not found").json_response(status_code=404)
    except todo_lists.TaskNotOwnedByUserError:
        return ErrorResponse(message="Task not owned by user").json_response(status_code=401)
    return SuccessResponse()
