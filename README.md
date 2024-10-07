# Local installation and run
1. Clone the repository
2. Install the dependencies: `poetry install`
3. Run migrations: `alembic upgrade head`
4. Run the application: `uvicorn src.api:app --reload`
# In Docker Compose
1. Clone the repository
2. Run the application: `docker compose up -d --build`
# Configuration
Configuration is done via environment variables (.env file). The following variables are available:
DEBUG - debug mode (default: True)
JWT_SECRET_KEY - secret key for JWT token (required)
DB_HOST - database host (required)
DB_PORT - database port (required)
DB_USER - database user (required)
DB_PASSWORD - database password (required)
DB_NAME - database name (required)
API_HOST - api host, needed for E2E tests (required)
API_PORT = api port, needed for E2E tests (required)
# Tests
Run the tests: `pytest`
E2E tests are located in `tests/e2e` directory.
Unit tests are located in `tests/unit` directory.
# API documentation
API documentation is available at `/docs` endpoint.