from flask import jsonify

from app.api.routes import main_bp


@main_bp.route("/healthz")
def healthcheck():
    return jsonify({
        "success": True,
        "status": "ok"
    })
