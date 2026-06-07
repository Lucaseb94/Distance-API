from app.models import RouteSummary


def get_home_data():
    sample_route = RouteSummary(
        origin="Origem",
        destination="Destino",
        distance_km=0.0,
    )

    return {
        "title": "Distance API",
        "message": "Estrutura Flask criada com sucesso.",
        "sample_route": sample_route,
    }
