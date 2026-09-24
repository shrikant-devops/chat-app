import logging

from flask import current_app, request
from flask_socketio import emit, join_room, leave_room

from . import db, socketio
from .metrics import CONNECTED_USERS, MESSAGES_SENT

log = logging.getLogger(__name__)

MAX_NAME = 32
MAX_BODY = 1000

# sid -> {"username": ..., "room": ...}
_sessions = {}


def _clean(value, max_len):
    return (value or "").strip()[:max_len]


@socketio.on("connect")
def on_connect():
    CONNECTED_USERS.inc()
    log.info("client connected sid=%s", request.sid)


@socketio.on("disconnect")
def on_disconnect(*_args):
    CONNECTED_USERS.dec()
    info = _sessions.pop(request.sid, None)
    if info:
        emit("system", {"body": f"{info['username']} left the room"}, to=info["room"])


@socketio.on("join")
def on_join(data):
    username = _clean(data.get("username"), MAX_NAME)
    room = _clean(data.get("room"), MAX_NAME).lower() or "general"
    if not username:
        emit("error", {"body": "Username is required"})
        return

    previous = _sessions.get(request.sid)
    if previous:
        leave_room(previous["room"])
        emit("system", {"body": f"{previous['username']} left the room"}, to=previous["room"])

    _sessions[request.sid] = {"username": username, "room": room}
    join_room(room)
    emit("history", db.recent_messages(room, current_app.config["HISTORY_LIMIT"]))
    emit("system", {"body": f"{username} joined #{room}"}, to=room)


@socketio.on("message")
def on_message(data):
    info = _sessions.get(request.sid)
    if not info:
        emit("error", {"body": "Join a room first"})
        return
    body = _clean(data.get("body"), MAX_BODY)
    if not body:
        return
    msg = db.save_message(info["room"], info["username"], body)
    MESSAGES_SENT.labels(info["room"]).inc()
    emit("message", msg, to=info["room"])


@socketio.on("typing")
def on_typing():
    info = _sessions.get(request.sid)
    if info:
        emit("typing", {"username": info["username"]}, to=info["room"], include_self=False)
