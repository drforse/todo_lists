import time
from pathlib import Path

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from src.db.orm_models import metadata
from src.utils import config


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope="function")
def postgres_db():
    engine = create_engine(config.get_sa_uri().replace("+asyncpg", ""))
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine

    # try:
    #     yield engine
    # finally:
    #     metadata.drop_all(engine)
    #     engine.dispose()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/api/__init__.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

