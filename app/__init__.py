from flask import Flask

from app.core.config import Config
from app.database import init_app as init_database
from app.routes import main_bp


def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")

    if Config.SECRET_KEY == "dev" and Config.IS_PRODUCTION:
        raise ValueError("SECRET_KEY é obrigatória em produção.")

    app.config.update(
        SECRET_KEY=Config.SECRET_KEY,
        MAX_CONTENT_LENGTH=Config.MAX_CONTENT_LENGTH,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=Config.IS_PRODUCTION,
    )

    if Config.DATABASE_PATH:
        app.config["DATABASE"] = Config.DATABASE_PATH

    init_database(app)
    app.register_blueprint(main_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    return app
