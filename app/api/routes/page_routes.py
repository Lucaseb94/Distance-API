from flask import redirect, render_template, session, url_for

from app.api.routes import main_bp
from app.core.config import Config
from app.services.auth_service import get_current_user
from app.services.home_service import get_home_data


@main_bp.route("/")
def index():
    return render_template(
        "index.html",
        data=get_home_data(),
        usuario=get_current_user(session.get("usuario_id")),
        google_maps_js_api_key=Config.GOOGLE_MAPS_JS_API_KEY or ""
    )


@main_bp.route("/login")
def login():
    return render_template("login.html")


@main_bp.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@main_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("main.login"))
