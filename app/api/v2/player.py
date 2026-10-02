from datetime import datetime, timezone
from typing import TypedDict, cast
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from core.websocket import WebsocketStore
from database.dependencies import db_session
from features.playback_state import PlaybackState, to_network_v2
from features.session.token import Token

from .shared import APIException, auth_required, auth_required_no_persist

player_router = APIRouter()

socket_store = WebsocketStore()


@player_router.get("/")
def get_player_state(token: Token = Depends(auth_required)):
    state = token.user.playback_state
    return to_network_v2(state) if state else None


class WSPacket(TypedDict):
    type: str
    data: dict


@player_router.websocket("/")
async def player_ws(
    websocket: WebSocket, token: Token = Depends(auth_required_no_persist)
):
    socket_id = socket_store.add_client(websocket)

    with db_session() as db:
        token = db.merge(token)
        state = token.user.playback_state
        if state is None:
            state = PlaybackState(
                user=token.user,
            )
            db.add(state)

    def expect_type(data, type: type):
        if not isinstance(data, type):
            raise APIException(
                code="INVAILD_PACKET_PROPERTIES",
                message=f"Expected {type.__name__}",
                status_code=400,
            )

        return data

    def expect_songs(ids):
        if not isinstance(ids, list):
            raise APIException(
                code="INVAILD_PACKET_PROPERTIES",
                message="Expected list of song ids",
                status_code=400,
            )

        song_ids = []
        for song_id in ids:
            if not isinstance(song_id, UUID):
                raise APIException(
                    code="INVAILD_PACKET_PROPERTIES",
                    message="Expected list of song ids",
                    status_code=400,
                )

            song_ids.append(song_id)

        return song_ids

    await websocket.accept()

    try:
        while True:
            json = await websocket.receive_json()
            packet: WSPacket
            try:
                packet = WSPacket(**json)
            except Exception:
                raise APIException(
                    code="INVAILD_PACKET",
                    message="Failed to parse packet",
                    status_code=400,
                )

            with db_session() as db:
                state = db.merge(state)

                match packet["type"]:
                    case "play":
                        state.paused_at = None
                        state.updated_at = datetime.now(timezone.utc)
                    case "pause":
                        state.paused_at = datetime.now(timezone.utc)
                    case "skip":
                        time = expect_type(packet["data"]["time"], float)

                        state.position = time
                        state.updated_at = datetime.now(timezone.utc)
                    case "shuffle":
                        active = expect_type(packet["data"]["active"], bool)
                        song_ids = expect_songs(packet["data"]["queue"])

                        state.queue = song_ids
                        state.shuffle_active = active
                    case "update":
                        queue = expect_songs(packet["data"]["queue"])
                        songs = expect_songs(packet["data"]["loaded"])

                        state.loaded_songs = songs
                        state.queue = queue
                    case "next":
                        state.queue.pop(0)
                    case "updateQueue":
                        queue = expect_songs(packet["data"]["queue"])
                        state.queue = queue
                    case _:
                        raise APIException(
                            code="INVAILD_PACKET",
                            message="Unknown packet type",
                            status_code=400,
                        )

                data = cast(dict, to_network_v2(state))

            await socket_store.broadcast(
                WSPacket(type="newState", data=data),
                websocket,
            )
    except WebSocketDisconnect:
        pass
    except APIException as e:
        await websocket.send_json(
            WSPacket(
                type="error",
                data={
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                    "status_code": e.status_code,
                },
            )
        )
    finally:
        socket_store.remove_client(socket_id)
