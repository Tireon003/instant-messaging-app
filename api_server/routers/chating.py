from fastapi import (
    APIRouter,
    Query,
    Cookie,
    Depends,
    Path,
)
from starlette.websockets import WebSocket, WebSocketDisconnect
from typing import Annotated

from api_server.core import database
from api_server.schemas import MessageFromDB, TokenPayload
from api_server.services import WebSocketManager, ChatService
from api_server.depends import get_chat_service, get_token_payload

router = APIRouter(
    prefix="/api/chats",
    tags=["Chats"]
)

manager = WebSocketManager()


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        chat_id: Annotated[int, Path()],
        to_user: Annotated[int, Query()],
        service: Annotated[
            ChatService,
            Depends(get_chat_service(database.get_async_session))
        ],
        token_payload: Annotated[TokenPayload, Depends(get_token_payload)]
):
    from_user_id = token_payload.sub
    tg_chat_id = token_payload.tg_chat_id
    await manager.connect(websocket, from_user_id)
    async with service.observe_chat(user_id=from_user_id, chat_id=chat_id):
        try:
            while True:
                message = (await websocket.receive_text()).strip()
                await service.send_message(
                    chat_id=chat_id,
                    tg_chat_id=tg_chat_id,
                    owner=from_user_id,
                    message=message,
                    to_user=to_user,
                )
                await manager.broadcast_personal_message(message, to_user)
        except WebSocketDisconnect:
            manager.disconnect(from_user_id)


@router.get("/", status_code=200, response_model=list[MessageFromDB])
async def get_chat_history(
        chat_id: Annotated[int, Query()],
        service: Annotated[
            ChatService,
            Depends(get_chat_service(database.get_async_session))
        ],
        token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> list[MessageFromDB] | None:
    user_id = token_payload.sub
    messages = await service.get_chat_history(
        chat_id=chat_id,
        user_id=user_id,
    )
    return messages
