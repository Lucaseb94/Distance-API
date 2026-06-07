from flask import request, session, url_for

from app.api.routes import main_bp
from app.api.routes.helpers import handle_app_error
from app.core.exceptions import AppError
from app.services.auth_service import authenticate_user, register_user
from app.utils.response_utils import success_response


@main_bp.route("/api/auth/cadastro", methods=["POST"])
def api_cadastro():
    try:
        usuario = register_user(request.get_json(silent=True) or {})
    except AppError as error:
        return handle_app_error(error)

    session.clear()
    session["usuario_id"] = usuario["id"]

    return success_response(
        {
            "redirect": url_for("main.index"),
            "usuario": usuario
        },
        message="Cadastro realizado com sucesso.",
        status=201
    )


@main_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    try:
        usuario = authenticate_user(request.get_json(silent=True) or {})
    except AppError as error:
        return handle_app_error(error)

    session.clear()
    session["usuario_id"] = usuario["id"]

    return success_response(
        {
            "redirect": url_for("main.index"),
            "usuario": usuario
        },
        message="Login realizado com sucesso."
    )


@main_bp.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return success_response(message="Logout realizado com sucesso.")
