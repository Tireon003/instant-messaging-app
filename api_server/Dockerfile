FROM python:3.12

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#COPY ../migrations ./migrations
#COPY ../alembic.ini .
COPY ../.env .
COPY ../api_server ./api_server

ENV PYTHONPATH=/app

#CMD alembic upgrade head & python3 server/main.py
CMD python3 api_server/main.py