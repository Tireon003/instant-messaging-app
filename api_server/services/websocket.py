import json
from typing import AsyncGenerator
from fastapi import WebSocket
import logging

from api_server.services import ChatService, UserService

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """Подключение нового WebSocket соединения по user_id."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info("User %s connected.", user_id)

    def disconnect(self, user_id: int) -> None:
        """Отключение WebSocket соединения для конкретного user_id."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info("User %s disconnected.", user_id)

    @staticmethod
    async def handle_messages(
            websocket: WebSocket,
            chat_service: ChatService,
            user_service: UserService,
            chat_id: int,
            from_user: int,
            to_user: int,
    ) -> AsyncGenerator[str, None]:
        sender_user = await user_service.get_user_from_db(from_user)
        recipient_user = await user_service.get_user_from_db(to_user)
        while True:
            message = await websocket.receive_text()
            message_json = await chat_service.send_message(
                chat_id=chat_id,
                from_user=sender_user,
                to_user=recipient_user,
                message=message.strip(),
            )
            yield message_json

    async def broadcast_personal_message(
            self,
            message_json: str,
            sender_id: int,
            recipient_id: int,
            chat_id: int,
    ) -> None:
        """Трансляция сообщения отправителю и получателю по их id"""
        message_dict = json.loads(message_json)
        message_for_chat_id = message_dict["chat_id"]
        websocket_sender = self.active_connections.get(sender_id)
        websocket_recipient = self.active_connections.get(recipient_id)
        if websocket_sender:
            await websocket_sender.send_text(message_json)
            logger.debug("Message was sent to client %s", sender_id)
        else:
            logger.info(
                "Message wasn't sent, client %s is offline.",
                sender_id
            )
        if websocket_recipient and message_for_chat_id == chat_id:
            await websocket_recipient.send_text(message_json)
            logger.debug("Message was sent to client %s", recipient_id)
        else:
            logger.info(
                "Message wasn't sent, client %s is offline.",
                recipient_id
            )
