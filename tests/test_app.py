import pytest

from app import create_app, socketio


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db")})


@pytest.fixture
def client(app):
    return app.test_client()


def _socket(app):
    return socketio.test_client(app, flask_test_client=app.test_client())


def test_index(client):
    assert client.get("/").status_code == 200


def test_health_and_ready(client):
    assert client.get("/health").get_json()["status"] == "ok"
    assert client.get("/ready").get_json()["status"] == "ready"


def test_metrics(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert b"chat_messages_total" in res.data


def test_join_and_message(app, client):
    alice, bob = _socket(app), _socket(app)
    alice.emit("join", {"username": "alice", "room": "DevOps"})
    bob.emit("join", {"username": "bob", "room": "devops"})
    alice.get_received()
    bob.get_received()

    alice.emit("message", {"body": "hello bob"})
    received = [e for e in bob.get_received() if e["name"] == "message"]
    assert received[0]["args"]["body"] == "hello bob"
    assert received[0]["args"]["username"] == "alice"

    history = client.get("/api/rooms/devops/messages").get_json()
    assert [m["body"] for m in history] == ["hello bob"]


def test_rooms_are_isolated(app):
    a, b = _socket(app), _socket(app)
    a.emit("join", {"username": "a", "room": "one"})
    b.emit("join", {"username": "b", "room": "two"})
    b.get_received()
    a.emit("message", {"body": "secret"})
    assert not [e for e in b.get_received() if e["name"] == "message"]


def test_message_requires_join(app):
    c = _socket(app)
    c.emit("message", {"body": "hi"})
    assert c.get_received()[-1]["name"] == "error"


def test_history_sent_on_join(app):
    a = _socket(app)
    a.emit("join", {"username": "a", "room": "hist"})
    a.emit("message", {"body": "first"})
    b = _socket(app)
    b.emit("join", {"username": "b", "room": "hist"})
    history = next(e for e in b.get_received() if e["name"] == "history")
    assert history["args"][0][0]["body"] == "first"  # history payload is a list
