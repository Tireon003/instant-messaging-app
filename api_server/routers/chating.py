from fastapi import (
    APIRouter,
    Query,
    Depends,
    Path,
    status,
    HTTPException,
    Body,
)
from fastapi.responses import (
    JSONResponse,
)
from starlette.websockets import (
    WebSocket,
    WebSocketDisconnect,
)
from typing import Annotated

from api_server.core import database
from api_server.exceptions import (
    ChatAlreadyExistException,
    NoSuchUserInDBException,
)
from api_server.schemas import (
    MessageFromDB,
    TokenPayload,
    ChatFromDB,
    ChatAndRecipient,
)
from api_server.services import (
    WebSocketManager,
    ChatService,
    UserService,
)
from api_server.dependencies import (
    get_chat_service,
    get_token_payload,
    get_user_service,
    get_token_payload_for_ws,
)

router = APIRouter(prefix="/api/chats", tags=["Chats"])

manager = WebSocketManager()


@router.websocket("/{chat_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: Annotated[int, Path()],
    to_user: Annotated[int, Query()],
    chat_service: Annotated[
        ChatService, Depends(get_chat_service(database.get_async_session))
    ],
    user_service: Annotated[
        UserService, Depends(get_user_service(database.get_async_session))
    ],
    token_payload: Annotated[TokenPayload, Depends(get_token_payload_for_ws)],
) -> None:
    from_user = token_payload.sub
    await manager.connect(websocket, from_user)
    async with chat_service.observe_chat(user_id=from_user, chat_id=chat_id):
        try:
            async for message_json in manager.handle_messages(
                websocket=websocket,
                chat_service=chat_service,
                user_service=user_service,
                chat_id=chat_id,
                from_user=from_user,
                to_user=to_user,
            ):
                await manager.broadcast_personal_message(
                    message_json=message_json,
                    sender_id=from_user,
                    recipient_id=to_user,
                    chat_id=chat_id,
                )
        except WebSocketDisconnect:
            manager.disconnect(from_user)


@router.get(
    "/{chat_id}/history",
    status_code=200,
    response_model=list[MessageFromDB],
    description="Getting chat history by chat id",
)
async def get_chat_history(
    chat_id: Annotated[int, Path()],
    service: Annotated[
        ChatService, Depends(get_chat_service(database.get_async_session))
    ],
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> list[MessageFromDB] | None:
    user_id = token_payload.sub
    messages = await service.get_chat_history(
        chat_id=chat_id,
        user_id=user_id,
    )
    return messages


@router.post(
    "/",
    status_code=201,
    response_model=ChatFromDB,
    description="Creating a new chat",
)
async def create_chat(
    chat_service: Annotated[
        ChatService, Depends(get_chat_service(database.get_async_session))
    ],
    user_service: Annotated[
        UserService, Depends(get_user_service(database.get_async_session))
    ],
    with_user: Annotated[str, Query()],
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> ChatFromDB:
    user_id = token_payload.sub
    try:
        recipient_id = await user_service.get_id_from_username(with_user)
        new_chat = await chat_service.create_new_chat(user_id, recipient_id)
        return new_chat
    except ChatAlreadyExistException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat is already exist",
        )
    except NoSuchUserInDBException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.get(
    "/",
    status_code=200,
    response_model=list[ChatAndRecipient],
    description="Getting user's list of his chats",
)
async def get_chat_list(
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
    service: Annotated[
        ChatService, Depends(get_chat_service(database.get_async_session))
    ],
) -> list[ChatAndRecipient]:
    user_id = token_payload.sub
    chat_list = await service.get_chat_list(user_id)
    return chat_list


@router.get(
    "/user_network_status",
    status_code=200,
    description="Getting user's network status (online/offline)",
)
async def get_user_network_status(
    recipient_id: Annotated[int, Query()],
) -> JSONResponse:
    online = recipient_id in manager.active_connections.keys()
    return JSONResponse(
        status_code=200, content={"status": "online" if online else "offline"}
    )


@router.post(
    "/get_read_status",
    status_code=status.HTTP_200_OK,
    response_model=dict[int, bool],
    description="Getting read status for provided messages",
)
async def get_read_status(
    chat_service: Annotated[
        ChatService, Depends(get_chat_service(database.get_async_session))
    ],
    messages: Annotated[list[int], Body()],
) -> JSONResponse:
    messages_read_status = await chat_service.get_read_status(messages)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=messages_read_status,
    )
