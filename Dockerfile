FROM python:3.10

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . .

CMD alembic upgrade head && uvicorn src.api:app --host 0.0.0.0 --port 8000