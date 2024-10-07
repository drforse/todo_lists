import datetime
import os
from dotenv import load_dotenv


load_dotenv()

DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]


def get_sa_uri():
    return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def alembic_sa_url():
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


JWT_ACCESS_TOKEN_EXPIRES_DELTA = datetime.timedelta(seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_DELTA", "3600")))
JWT_REFRESH_TOKEN_EXPIRES_DELTA = datetime.timedelta(seconds=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DELTA", "3600")))


API_HOST = os.environ["API_HOST"]
API_PORT = os.environ["API_PORT"]

def get_api_url():
    return f"http://{API_HOST}:{API_PORT}"
