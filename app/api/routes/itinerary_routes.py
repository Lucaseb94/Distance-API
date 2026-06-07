from flask import request

from app.api.routes import main_bp
from app.api.routes.helpers import handle_app_error, require_login
from app.core.exceptions import AppError
from app.services.itinerary_service import ItineraryService
from app.utils.response_utils import success_response


@main_bp.route("/api/rotas/itinerario", methods=["POST"])
def calcular_itinerario():
    usuario_id, login_error = require_login("Faça login para calcular itinerários.")

    if login_error:
        return login_error

    try:
        resultado = ItineraryService().calculate_itinerary(
            request.get_json(silent=True) or {},
            usuario_id
        )
    except AppError as error:
        return handle_app_error(error)

    return success_response(
        resultado,
        message="Itinerário calculado com sucesso."
    )
