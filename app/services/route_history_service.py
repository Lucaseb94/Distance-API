from app.database import get_db


def save_simple_route(usuario_id, payload, resultado):
    origem = resultado["origem"]
    destino = resultado["destino"]

    get_db().execute(
        """
        INSERT INTO rotas (
            usuario_id,
            cep_origem,
            numero_origem,
            endereco_origem,
            origem_lat,
            origem_lng,
            cep_destino,
            numero_destino,
            endereco_destino,
            destino_lat,
            destino_lng,
            distancia_km,
            duracao_min,
            polyline
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            usuario_id,
            payload["cep_origem"],
            payload["numero_origem"],
            origem.get("endereco"),
            origem.get("lat"),
            origem.get("lng"),
            payload["cep_destino"],
            payload["numero_destino"],
            destino.get("endereco"),
            destino.get("lat"),
            destino.get("lng"),
            resultado.get("distancia_km"),
            resultado.get("duracao_min"),
            resultado.get("polyline")
        )
    )
    get_db().commit()


def save_itinerary(usuario_id, resultado):
    paradas = resultado["paradas"]
    origem = paradas[0]
    destino = paradas[-1]
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO rotas (
            usuario_id,
            cep_origem,
            numero_origem,
            endereco_origem,
            origem_lat,
            origem_lng,
            cep_destino,
            numero_destino,
            endereco_destino,
            destino_lat,
            destino_lng,
            distancia_km,
            duracao_min,
            polyline
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            usuario_id,
            origem.get("cep"),
            origem.get("numero"),
            origem.get("endereco"),
            origem.get("lat"),
            origem.get("lng"),
            destino.get("cep"),
            destino.get("numero"),
            destino.get("endereco"),
            destino.get("lat"),
            destino.get("lng"),
            resultado.get("distancia_km"),
            resultado.get("duracao_min"),
            resultado.get("polyline")
        )
    )
    rota_id = cursor.lastrowid

    for parada in paradas:
        db.execute(
            """
            INSERT INTO rota_paradas (
                rota_id,
                ordem,
                cep,
                numero,
                endereco,
                lat,
                lng
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rota_id,
                parada.get("ordem"),
                parada.get("cep"),
                parada.get("numero"),
                parada.get("endereco"),
                parada.get("lat"),
                parada.get("lng")
            )
        )

    db.commit()
