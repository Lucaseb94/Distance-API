from sqlite3 import IntegrityError

from werkzeug.security import check_password_hash, generate_password_hash

from app.core.exceptions import AuthError, ValidationError
from app.database import get_db
from app.schemas.auth_schema import LoginRequest, RegisterRequest


def register_user(payload):
    data = RegisterRequest.from_payload(payload)
    db = get_db()

    if email_already_registered(data.email):
        raise ValidationError("Este e-mail já está cadastrado.", status_code=409)

    try:
        cursor = db.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (?, ?, ?)
            """,
            (data.nome, data.email, generate_password_hash(data.senha))
        )
        db.commit()
    except IntegrityError as exc:
        raise ValidationError("Este e-mail já está cadastrado.", status_code=409) from exc

    return {
        "id": cursor.lastrowid,
        "nome": data.nome,
        "email": data.email
    }


def email_already_registered(email):
    usuario = get_db().execute(
        """
        SELECT id
        FROM usuarios
        WHERE lower(email) = lower(?)
        LIMIT 1
        """,
        (email,)
    ).fetchone()

    return usuario is not None


def authenticate_user(payload):
    data = LoginRequest.from_payload(payload)
    usuario = get_db().execute(
        """
        SELECT id, nome, email, senha_hash
        FROM usuarios
        WHERE email = ?
        """,
        (data.email,)
    ).fetchone()

    if usuario is None or not check_password_hash(usuario["senha_hash"], data.senha):
        raise AuthError("E-mail ou senha inválidos.")

    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"]
    }


def get_current_user(usuario_id):
    if not usuario_id:
        return None

    usuario = get_db().execute(
        """
        SELECT id, nome, email
        FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,)
    ).fetchone()

    return dict(usuario) if usuario else None
