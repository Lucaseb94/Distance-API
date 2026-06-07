from flask import current_app, session, url_for

from app.core.exceptions import AppError
from app.utils.response_utils import error_response


def require_login(message):
    usuario_id = session.get("usuario_id")

    if usuario_id:
        return usuario_id, None

    response = error_response(
        message,
        status=401,
        extra={"redirect": url_for("main.login")}
    )
    return None, response


def handle_app_error(error):
    extra = {}

    if error.status_code == 401:
        extra["redirect"] = url_for("main.login")

    return error_response(
        error.message,
        status=error.status_code,
        errors=error.errors,
        extra=extra
    )


def handle_unexpected_error(error):
    current_app.logger.exception("Erro inesperado na aplicação")
    return error_response(
        "Erro interno da aplicação.",
        status=500
    )
