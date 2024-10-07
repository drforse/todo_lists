import logging

from fastapi import FastAPI

from src.utils import config
from src.db import orm_models


def _app():
    logging.basicConfig(level=logging.INFO)

    orm_models.start_mappers()

    app_ = FastAPI(debug=config.DEBUG)

    # configure cors if needed

    from .endpoints import routers
    for router in routers:
        app_.include_router(router)

    return app_

app = _app()
