import logging
import os

from flask import Flask
from flask_socketio import SocketIO

from . import db

socketio = SocketIO()


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        DATABASE_PATH=os.environ.get("DATABASE_PATH", "chat.db"),
        HISTORY_LIMIT=int(os.environ.get("HISTORY_LIMIT", "50")),
        APP_VERSION=os.environ.get("APP_VERSION", "dev"),
    )
    if config:
        app.config.update(config)

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    from . import events  # noqa: F401  registers socket handlers

    socketio.init_app(app, cors_allowed_origins=os.environ.get("CORS_ORIGINS", "*"))
    return app
