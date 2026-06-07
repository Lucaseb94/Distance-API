import os

from dotenv import load_dotenv


load_dotenv()


def get_int_env(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev"
    ENVIRONMENT = (
        os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development"
    ).lower()
    IS_PRODUCTION = ENVIRONMENT == "production"
    MAX_CONTENT_LENGTH = get_int_env("MAX_CONTENT_LENGTH", 32768)
    DEMO_ROUTE_LIMIT = get_int_env("DEMO_ROUTE_LIMIT", 4)
    DATABASE_PATH = os.getenv("DATABASE_PATH")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    GOOGLE_MAPS_JS_API_KEY = os.getenv("GOOGLE_MAPS_JS_API_KEY")
    GOOGLE_ROUTES_URL = os.getenv(
        "GOOGLE_ROUTES_URL",
        "https://routes.googleapis.com/directions/v2:computeRoutes"
    )
    VIACEP_URL_TEMPLATE = "https://viacep.com.br/ws/{cep}/json/"
