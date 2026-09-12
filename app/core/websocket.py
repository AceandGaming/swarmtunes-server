import asyncio
import secrets
from typing import Any

from fastapi.websockets import WebSocket


class WebsocketStore:
    clients: dict[str, WebSocket]

    def __init__(self):
        self.clients = {}

    def add_client(self, client: WebSocket):
        id = None
        while not id or id in self.clients:
            id = secrets.token_hex(8)

        self.clients[id] = client
        return id

    def remove_client(self, id: str):
        if id in self.clients:
            del self.clients[id]

    async def broadcast(self, message: Any, exclude=None):
        return await asyncio.gather(
            *[
                self.send(client, message)
                for client in self.clients.values()
                if client != exclude
            ]
        )

    async def send(self, client: WebSocket, message: Any):
        return await client.send_json({"data": message})
