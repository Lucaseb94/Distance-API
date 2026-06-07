from app.providers.cep_provider import BuscaCEP
from app.services.google_routes_service import GoogleRoute


def imprimir_erro_endereco(tipo, resultado):
    print(f"Erro no endereço de {tipo}: {resultado.get('error')}")


def main():
    busca = BuscaCEP()

    origem = busca.buscar_endereco("04851706", numero="67")
    destino = busca.buscar_endereco("01140-060", numero="399")

    if not origem["valido"]:
        imprimir_erro_endereco("origem", origem)
        return

    if not destino["valido"]:
        imprimir_erro_endereco("destino", destino)
        return

    print("Origem:", origem["endereco_google"])
    print("Destino:", destino["endereco_google"])

    try:
        google_routes = GoogleRoute()
    except ValueError as e:
        print(f"Erro de configuração: {e}")
        return

    resultado = google_routes.calcular_menor_rota(
        origem["endereco_google"],
        destino["endereco_google"]
    )

    print("Resultado da consulta Google Routes API:")
    print(resultado)


if __name__ == "__main__":
    main()
