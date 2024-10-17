FROM python:3.12

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../migrations ./migrations
COPY ../alembic.ini .
COPY ../.env .
COPY ../api_server ./api_server

ENV PYTHONPATH=/app

CMD alembic upgrade head;celery -A api_server.tasks.notification_tasks:celery worker --loglevel=INFO & python3 api_server/main.py