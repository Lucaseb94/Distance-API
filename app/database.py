import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema_path = Path(current_app.root_path) / "schema.sql"

    with schema_path.open("r", encoding="utf-8") as schema_file:
        db.executescript(schema_file.read())


def init_app(app):
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    if not app.config.get("DATABASE"):
        app.config["DATABASE"] = str(instance_path / "distance_api.sqlite")

    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
