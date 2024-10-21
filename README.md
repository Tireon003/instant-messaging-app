# instant-messaging-service

A simple service for exchanging instant messages between users in real time.

### Functionality:
1. Authentication and authorization based on OAuth2 with JWT session tokens
2. Creating chats with users
3. Communication in real time with saving history in the database and subsequent loading
4. Automatic notifications about missed messages from users via a telegram bot when the user is offline

### Stack
- SPA: Vite, JavaScript, React, Nginx, HTML5, Tailwind CSS, React-router, axios
- API: Python, REST API, FastAPI, Pydantic v2, SQLAlchemy v2, Alembic, Redis, Celery, Aiogram3, WebSockets, PostgreSQL
- Telegram bot: Aiogram3, Aiohttp

### How to run

1. Install Docker (if not installed)
2. Install Git (if not installed)
3. Open terminal and open the folder where you want to place the project
4. Enter command:
```shell
git clone https://github.com/Tireon003/instant-messaging-service
```
5. Enter to project folder and create .env file. It should contain the next variables:
```editorconfig
BOT_TOKEN=<api_key_of_your_tg_bot>

DB_NAME=<database_name>
DB_HOST=msg_db  // don't touch
DB_USER=<postgres_user>
DB_PORT=<postgres_server_port>
DB_PASS=<password_for_postgres>

API_HOST=<host_for_api_server>
API_PORT=<port_for_api_server>

JWT_SECRET=<secret_key_use_difficult>

LOG_LEVEL="INFO" //you can change log level if want
```
6. Enter command to build and start app:
```shell
docker-compose up -d --build
```
7. Wait for the project to be built

Well, now application is available on url:
```text
http://locallost:8080/  # react app
http://localhost:8080/docs  # fastapi docs
```
The next url's are available:
 - /login - page for log in
 - /register - page for sign up
 - /chat - Main page for chatting
