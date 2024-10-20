from fastapi import (
    APIRouter,
    Query,
    Depends,
    Path,
    status,
    HTTPException,
)
from starlette.websockets import WebSocket, WebSocketDisconnect
from typing import Annotated

from api_server.core import database
from api_server.exceptions import ChatAlreadyExistException
from api_server.schemas import (
    MessageFromDB,
    TokenPayload,
    ChatFromDB,
    ChatAndRecipient,
)
from api_server.services import WebSocketManager, ChatService, UserService
from api_server.depends import (
    get_chat_service,
    get_token_payload,
    get_user_service,
    get_token_for_ws,
)

router = APIRouter(
    prefix="/api/chats",
    tags=["Chats"]
)

manager = WebSocketManager()


@router.websocket("/{chat_id}/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        chat_id: Annotated[int, Path()],
        to_user: Annotated[int, Query()],
        chat_service: Annotated[
            ChatService,
            Depends(get_chat_service(database.get_async_session))
        ],
        user_service: Annotated[
            UserService,
            Depends(get_user_service(database.get_async_session))
        ],
        token_payload: Annotated[TokenPayload, Depends(get_token_for_ws)]
):
    from_user_id = token_payload.sub
    tg_chat_id = await user_service.get_recipient_tg_chat_id(to_user)
    recipient_username = await user_service.get_username(from_user_id)
    await manager.connect(websocket, from_user_id)
    async with chat_service.observe_chat(user_id=from_user_id, chat_id=chat_id):
        try:
            while True:
                message = (await websocket.receive_text()).strip()
                message_json = await chat_service.send_message(
                    chat_id=chat_id,
                    tg_chat_id=tg_chat_id,
                    owner=from_user_id,
                    message=message,
                    to_user=to_user,
                    to_user_username=recipient_username,
                )
                await manager.broadcast_personal_message(message_json, to_user)
        except WebSocketDisconnect:
            manager.disconnect(from_user_id)


@router.get("/{chat_id}/history",
            status_code=200,
            response_model=list[MessageFromDB])
async def get_chat_history(
        chat_id: Annotated[int, Path()],
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


@router.post("/", status_code=201, response_model=ChatFromDB)
async def create_chat(
        chat_service: Annotated[
            ChatService,
            Depends(get_chat_service(database.get_async_session))
        ],
        user_service: Annotated[
            UserService,
            Depends(get_user_service(database.get_async_session))
        ],
        with_user: Annotated[str, Query()],
        token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> ChatFromDB:
    user_id = token_payload.sub
    try:
        with_user_id = await user_service.get_id_from_username(with_user)
        if not with_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        new_chat = await chat_service.create_new_chat(user_id, with_user_id)
        return new_chat
    except ChatAlreadyExistException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat is already exist",
        )


@router.get("/",
            status_code=200,
            response_model=list[ChatAndRecipient])
async def get_chat_list(
        token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
        service: Annotated[
            ChatService,
            Depends(get_chat_service(database.get_async_session))
        ],
) -> list[ChatAndRecipient]:
    user_id = token_payload.sub
    chat_list = await service.get_chat_list(user_id)
    return chat_list
