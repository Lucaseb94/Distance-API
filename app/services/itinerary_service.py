from app.core.exceptions import ExternalApiError
from app.schemas.itinerary_schema import ItineraryRequest
from app.services.google_routes_service import GoogleRoute
from app.services.address_service import AddressService
from app.services.route_history_service import save_itinerary
from app.services.route_optimizer_service import combine_stops_with_route


class ItineraryService:
    def __init__(self, address_service=None, google_routes=None):
        self.address_service = address_service or AddressService()
        self.google_routes = google_routes

    def calculate_itinerary(self, payload, usuario_id):
        data = ItineraryRequest.from_payload(payload)
        stops = self.build_stops(data.paradas)
        route = self.calculate_route_by_mode(
            [stop["endereco"] for stop in stops],
            data.modo_destino
        )
        ordered_stops = combine_stops_with_route(
            stops,
            route["paradas"],
            final_order_indexes=route.get("indices_ordem_final"),
            intermediate_order=route.get("ordem_intermediarios", [])
        )
        result = self.build_response(data.modo_destino, ordered_stops, stops, route)
        save_itinerary(usuario_id, result)
        return result

    def build_stops(self, stop_requests):
        stops = []

        for index, stop in enumerate(stop_requests):
            address = self.address_service.resolve_stop(stop, index)
            stops.append({
                "ordem": index + 1,
                "cep": address["cep_formatado"],
                "numero": stop.numero,
                "endereco": address["endereco_google"]
            })

        return stops

    def calculate_route_by_mode(self, addresses, destination_mode):
        google_routes = self.get_google_routes()

        if destination_mode == "automatico":
            route = google_routes.calcular_rota_com_destino_automatico(addresses)
        else:
            route = google_routes.calcular_rota_com_destino_fixo(
                addresses,
                otimizar=True
            )

        if not route.get("valido"):
            raise ExternalApiError(
                route.get("error", "Não foi possível calcular o itinerário."),
                errors=[{
                    "field": "google_routes",
                    "detail": route.get("detalhes") or route.get("error")
                }]
            )

        return route

    def build_response(self, destination_mode, ordered_stops, original_stops, route):
        return {
            "origem": ordered_stops[0],
            "destino": ordered_stops[-1],
            "destino_escolhido": ordered_stops[-1],
            "paradas": ordered_stops,
            "ordem_original": original_stops,
            "ordem_otimizada": ordered_stops,
            "trechos": route.get("trechos", []),
            "distancia_km": route.get("distancia_km"),
            "duracao_min": route.get("duracao_minutos"),
            "duracao_segundos": route.get("duracao_segundos"),
            "polyline": route.get("polyline"),
            "modo_destino": destination_mode,
            "ordem_intermediarios": route.get("ordem_intermediarios", []),
            "indices_ordem_final": route.get("indices_ordem_final", []),
            "indice_destino_escolhido": route.get("indice_destino_escolhido"),
            "rotas_avaliadas": route.get("rotas_avaliadas"),
            "otimizado": route.get("otimizado", False),
            "criterio_rota": route.get("criterio_rota")
        }

    def get_google_routes(self):
        if self.google_routes:
            return self.google_routes

        try:
            self.google_routes = GoogleRoute()
        except ValueError as exc:
            raise ExternalApiError(str(exc), status_code=500) from exc

        return self.google_routes
