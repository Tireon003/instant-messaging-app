from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api_server.config import settings
from api_server.routers import auth_router

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app = FastAPI(
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )
