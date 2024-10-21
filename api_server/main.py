import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from api_server.config import settings
from api_server.logs import configure_logging
from api_server.routers import auth_router, chating_router
from api_server.exceptions import (
    NoSuchUserInDBException,
    WrongPasswordException,
    UserAlreadyExistException,
    InvalidCodeException,
    InvalidSessionKeyException,
)

origins = [
    "*"
]

logger = logging.getLogger(__name__)


app = FastAPI(
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chating_router)


@app.exception_handler(NoSuchUserInDBException)
async def handle_no_such_user_exception(
        request: Request,
        exc: NoSuchUserInDBException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content="User with such username doesn't exists",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(WrongPasswordException)
async def handle_wrong_pass_exception(
        request: Request,
        exc: WrongPasswordException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content="User entered wrong password",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(UserAlreadyExistException)
async def handle_user_already_exist_exception(
        request: Request,
        exc: UserAlreadyExistException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="User with such username already exists",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(InvalidCodeException)
async def handle_invalid_code_exception(
        request: Request,
        exc: InvalidCodeException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="Invalid code provided",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(InvalidSessionKeyException)
async def handle_invalid_code_exception(
        request: Request,
        exc: InvalidSessionKeyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="Invalid session token provided",
        headers={"WWW-Authenticate": "Bearer"}
    )


def main():
    configure_logging(level=settings.LOG_LEVEL)
    logger.info("Starting uvicorn app")
    uvicorn.run(
        app=app,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )
    logger.info("Finished uvicorn app")


if __name__ == '__main__':
    main()
