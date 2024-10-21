from typing import Dict
from fastapi import WebSocket
import logging

from api_server.services import ChatService, UserService

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение нового WebSocket соединения по user_id."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info("User %s connected.", user_id)

    def disconnect(self, user_id: int):
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
    ) -> None:
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

    async def broadcast_personal_message(self, message: str, user_id: int):
        """Отправка сообщения конкретному пользователю по его user_id."""
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)
            logger.debug("Message was sent to client %s", user_id)
        else:
            logger.info(
                "Message wasn't sent, client %s is offline.",
                user_id
            )
