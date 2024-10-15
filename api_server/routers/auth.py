from fastapi import (
    APIRouter,
)
from fastapi.responses import (
    JSONResponse,
)

from api_server.schemas import UserLogin

router = APIRouter(
    prefix='/api/auth',
    tags=['auth'],
)


@router.post("/login", status_code=200)
async def login_user(user_login_data: UserLogin) -> JSONResponse:
    ...
