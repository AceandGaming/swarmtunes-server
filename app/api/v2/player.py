import asyncio

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from core.websocket import WebsocketStore
from database.dependencies import db_session
from features.playback_state import PlaybackState, to_network_v2
from features.session.token import Token

from .shared import APIException, auth_required

player_router = APIRouter()

socket_store = WebsocketStore()


@player_router.get("/")
def get_player_state(token: Token = Depends(auth_required)):
    state = token.user.playback_state
    return to_network_v2(state) if state else None


@player_router.websocket("/")
async def player_ws(websocket: WebSocket, token=Depends(auth_required)):
    socket_id = socket_store.add_client(websocket)

    await websocket.accept()
    try:
        while True:
            await socket_store.broadcast({"type": "test"})

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    except APIException as e:
        await websocket.send_json(
            {
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                },
                "status_code": e.status_code,
            }
        )
    finally:
        socket_store.remove_client(socket_id)
