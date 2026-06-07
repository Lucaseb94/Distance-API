from flask import Blueprint


main_bp = Blueprint("main", __name__)


from app.api.routes import auth_routes, health_routes, itinerary_routes, page_routes, route_routes  # noqa: E402,F401
