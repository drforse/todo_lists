import string
import random
import uuid

import pytest
import requests

from src.utils import config


def create_user(username: str = None, password: str = None):
    username = username or "".join(random.choices(string.ascii_letters, k=10)),
    password = password or "".join(random.choices(string.ascii_letters, k=10))
    url = config.get_api_url()
    response = requests.post(
        f"{url}/sign-up",
        data={"username": username, "password": password, "repeat_password": password},
    )
    return response.json()["result"]["token"]


def create_tasks(access_token: str, count: int = 2):
    url = config.get_api_url()
    for i in range(count):
        response = requests.post(
            f"{url}/tasks/create",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"datetime_to_do": "2022-01-01T00:00:00", "task_info": f"Test task {i}"},
        )
        assert response.status_code == 201


def get_tasks_list(access_token: str):
    url = config.get_api_url()
    response = requests.get(
        f"{url}/tasks/list",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()["result"]


def get_task(access_token: str, task_id: str):
    url = config.get_api_url()
    response = requests.get(
        f"{url}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()["result"]


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_sign_up():
    username = "".join(random.choices(string.ascii_letters, k=10))
    password = "".join(random.choices(string.ascii_letters, k=10))
    url = config.get_api_url()
    response = requests.post(
        f"{url}/sign-up",
        data={"username": username, "password": password, "repeat_password": password},
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert "token" in result
    assert "refresh_token" in result
    check_auth_response = requests.get(
        f"{url}/test-access-token",
        headers={"Authorization": f"Bearer {result['token']}"},
    )
    assert check_auth_response.status_code == 200
    assert check_auth_response.json()["success"] is True


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_sign_in():
    username = "".join(random.choices(string.ascii_letters, k=10))
    password = "".join(random.choices(string.ascii_letters, k=10))
    access_token = create_user(username, password)
    url = config.get_api_url()
    response = requests.post(
        f"{url}/sign-in",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert "token" in result
    assert "refresh_token" in result
    check_auth_response = requests.get(
        f"{url}/test-access-token",
        headers={"Authorization": f"Bearer {result['token']}"},
    )
    assert check_auth_response.status_code == 200
    assert check_auth_response.json()["success"] is True


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_sign_in_wrong_password():
    username = "".join(random.choices(string.ascii_letters, k=10))
    password = "".join(random.choices(string.ascii_letters, k=10))
    access_token = create_user(username, password)
    url = config.get_api_url()
    response = requests.post(
        f"{url}/sign-in",
        data={"username": username, "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid password"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_sign_in_wrong_username():
    username = "".join(random.choices(string.ascii_letters, k=10))
    password = "".join(random.choices(string.ascii_letters, k=10))
    access_token = create_user(username, password)
    url = config.get_api_url()
    response = requests.post(
        f"{url}/sign-in",
        data={"username": "wrong", "password": password},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "User wrong not found"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_create_task():
    access_token = create_user()
    url = config.get_api_url()
    response = requests.post(
        f"{url}/tasks/create",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"datetime_to_do": "2022-01-01T00:00:00", "task_info": "Test task"},
    )
    assert response.status_code == 201
    assert response.json()["success"] is True


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_get_tasks_list():
    access_token = create_user()
    create_tasks(access_token)
    url = config.get_api_url()
    response = requests.get(
        f"{url}/tasks/list",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()["result"]) == 2


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_get_task():
    access_token = create_user()
    create_tasks(access_token)
    tasks = get_tasks_list(access_token)
    url = config.get_api_url()
    response = requests.get(
        f"{url}/tasks/{tasks[0]['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["result"]["info"] == "Test task 0"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_get_task_not_owned():
    access_token = create_user()
    create_tasks(access_token)
    tasks = get_tasks_list(access_token)
    access_token_2 = create_user()
    url = config.get_api_url()
    response = requests.get(
        f"{url}/tasks/{tasks[0]['id']}",
        headers={"Authorization": f"Bearer {access_token_2}"},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Task not owned by user"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_get_task_not_found():
    access_token = create_user()
    url = config.get_api_url()
    response = requests.get(
        f"{url}/tasks/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["message"] == "Task not found"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_update_task():
    access_token = create_user()
    create_tasks(access_token)
    tasks = get_tasks_list(access_token)
    url = config.get_api_url()
    response = requests.patch(
        f"{url}/tasks/{tasks[0]['id']}/update",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"datetime_to_do": "2022-01-01T00:00:00", "task_info": "Updated task"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    task = get_task(access_token, tasks[0]["id"])
    assert task["info"] == "Updated task"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_update_task_not_owned():
    access_token = create_user()
    create_tasks(access_token)
    tasks = get_tasks_list(access_token)
    access_token_2 = create_user()
    url = config.get_api_url()
    response = requests.patch(
        f"{url}/tasks/{tasks[0]['id']}/update",
        headers={"Authorization": f"Bearer {access_token_2}"},
        json={"datetime_to_do": "2022-01-01T00:00:00", "task_info": "Updated task"},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Task not owned by user"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_update_task_not_found():
    access_token = create_user()
    url = config.get_api_url()
    response = requests.patch(
        f"{url}/tasks/{uuid.uuid4()}/update",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"datetime_to_do": "2022-01-01T00:00:00", "task_info": "Updated task"},
    )
    assert response.status_code == 404
    assert response.json()["message"] == "Task not found"
