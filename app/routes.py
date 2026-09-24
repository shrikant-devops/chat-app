from flask import Blueprint, Response, current_app, jsonify, render_template, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import db
from .metrics import HTTP_REQUESTS

bp = Blueprint("main", __name__)


@bp.after_app_request
def count_request(response):
    HTTP_REQUESTS.labels(request.method, request.endpoint or "unknown", response.status_code).inc()
    return response


@bp.get("/")
def index():
    return render_template("index.html", version=current_app.config["APP_VERSION"])


@bp.get("/health")
def health():
    """Liveness probe: the process is up."""
    return jsonify(status="ok", version=current_app.config["APP_VERSION"])


@bp.get("/ready")
def ready():
    """Readiness probe: dependencies (database) are reachable."""
    try:
        db.ping()
    except Exception as exc:  # noqa: BLE001
        return jsonify(status="unavailable", error=str(exc)), 503
    return jsonify(status="ready")


@bp.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@bp.get("/api/rooms/<room>/messages")
def room_messages(room):
    limit = min(request.args.get("limit", current_app.config["HISTORY_LIMIT"], type=int), 200)
    return jsonify(db.recent_messages(room, limit))
