from flask import jsonify


def success_response(data=None, message="Operação realizada com sucesso.", status=200):
    data = data or {}
    payload = {
        "success": True,
        "data": data,
        "message": message,
        "errors": [],
        "valido": True
    }

    if isinstance(data, dict):
        payload.update(data)

    return jsonify(payload), status


def error_response(message, status=400, errors=None, extra=None):
    payload = {
        "success": False,
        "data": None,
        "message": message,
        "errors": errors or [],
        "valido": False,
        "error": message
    }

    if extra:
        payload.update(extra)

    return jsonify(payload), status


def route_error_response(error):
    extra = {}

    for campo in ("status_code", "detalhes"):
        if error.get(campo) is not None:
            extra[campo] = error.get(campo)

    return error_response(
        error.get("error", "Não foi possível calcular a rota."),
        status=502,
        extra=extra
    )
