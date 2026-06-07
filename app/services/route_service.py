from app.core.exceptions import ExternalApiError
from app.schemas.route_schema import SimpleRouteRequest
from app.services.google_routes_service import GoogleRoute
from app.services.address_service import AddressService
from app.services.route_history_service import save_simple_route


class RouteService:
    def __init__(self, address_service=None, google_routes=None):
        self.address_service = address_service or AddressService()
        self.google_routes = google_routes

    def calculate_simple_route(self, payload, usuario_id):
        data = SimpleRouteRequest.from_payload(payload)
        origem = self.address_service.resolve(
            data.cep_origem,
            numero=data.numero_origem,
            label="Origem"
        )
        destino = self.address_service.resolve(
            data.cep_destino,
            numero=data.numero_destino,
            label="Destino"
        )
        google_routes = self.get_google_routes()
        rota = google_routes.calcular_menor_rota(
            origem["endereco_google"],
            destino["endereco_google"]
        )

        if not rota.get("valido"):
            raise ExternalApiError(
                rota.get("error", "Não foi possível calcular a rota."),
                errors=[{
                    "field": "google_routes",
                    "detail": rota.get("detalhes") or rota.get("error")
                }]
            )

        resultado = {
            "origem": {
                "endereco": origem["endereco_google"],
                "lat": rota.get("origem_lat"),
                "lng": rota.get("origem_lng")
            },
            "destino": {
                "endereco": destino["endereco_google"],
                "lat": rota.get("destino_lat"),
                "lng": rota.get("destino_lng")
            },
            "distancia_km": rota.get("distancia_km"),
            "duracao_min": rota.get("duracao_minutos"),
            "polyline": rota.get("polyline")
        }
        save_simple_route(usuario_id, data.to_legacy_payload(), resultado)
        return resultado

    def get_google_routes(self):
        if self.google_routes:
            return self.google_routes

        try:
            self.google_routes = GoogleRoute()
        except ValueError as exc:
            raise ExternalApiError(str(exc), status_code=500) from exc

        return self.google_routes
