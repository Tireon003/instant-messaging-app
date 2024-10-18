from typing import Dict
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        # Словарь для хранения сокетов, где ключом будет user_id, а значением — WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение нового WebSocket соединения по user_id."""
        await websocket.accept()  # Принять подключение WebSocket
        self.active_connections[user_id] = websocket  # Сохраняем сокет в словарь
        print(f"User {user_id} connected.")  # Лог подключения

    def disconnect(self, user_id: int):
        """Отключение WebSocket соединения для конкретного user_id."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]  # Удаляем сокет из словаря
            print(f"User {user_id} disconnected.")  # Лог отключения

    async def broadcast_personal_message(self, message: str, user_id: int):
        """Отправка сообщения конкретному пользователю по его user_id."""
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)  # Отправка текстового сообщения
            print(f"Sent message to User {user_id}: {message}")
        else:
            print(f"User {user_id} is not connected.")  # Лог, если пользователь не подключен
