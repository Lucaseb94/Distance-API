from flask import request

from app.api.routes import main_bp
from app.api.routes.helpers import handle_app_error, require_login
from app.core.exceptions import AppError
from app.services.route_service import RouteService
from app.utils.response_utils import success_response


@main_bp.route("/api/rotas/calcular", methods=["POST"])
def calcular_rota():
    usuario_id, login_error = require_login("Faça login para calcular rotas.")

    if login_error:
        return login_error

    try:
        resultado = RouteService().calculate_simple_route(
            request.get_json(silent=True) or {},
            usuario_id
        )
    except AppError as error:
        return handle_app_error(error)

    return success_response(
        resultado,
        message="Rota calculada com sucesso."
    )
