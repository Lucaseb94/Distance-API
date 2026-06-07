from flask import Flask

from app.core.config import Config
from app.database import init_app as init_database
from app.routes import main_bp


def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")

    if Config.SECRET_KEY == "dev" and Config.ENVIRONMENT == "production":
        raise ValueError("SECRET_KEY é obrigatória em produção.")

    app.config["SECRET_KEY"] = Config.SECRET_KEY

    if Config.DATABASE_PATH:
        app.config["DATABASE"] = Config.DATABASE_PATH

    init_database(app)
    app.register_blueprint(main_bp)
    return app
