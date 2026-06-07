from datetime import datetime, timedelta, timezone

import requests

from app.core.config import Config
from app.providers.google_routes_provider import GoogleRoutesProvider


class GoogleRoute:
    def __init__(self):
        self.api_key = Config.GOOGLE_MAPS_API_KEY
        self.url = Config.GOOGLE_ROUTES_URL

        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY não encontrada nas variáveis de ambiente")

        self.provider = GoogleRoutesProvider(api_key=self.api_key, url=self.url)

    def calcular_menor_rota(self, origem, destino):
        if not origem:
            return {"valido": False, "error": "Endereço de origem é obrigatório."}

        if not destino:
            return {"valido": False, "error": "Endereço de destino é obrigatório."}

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "routes.distanceMeters,"
                "routes.duration,"
                "routes.staticDuration,"
                "routes.description,"
                "routes.routeLabels,"
                "routes.polyline.encodedPolyline,"
                "routes.legs.startLocation,"
                "routes.legs.endLocation"
            )
        }

        body = {
            "origin": {
                "address": origem
            },
            "destination": {
                "address": destino
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_UNAWARE",
            "computeAlternativeRoutes": True,
            "languageCode": "pt-BR",
            "regionCode": "BR",
            "units": "METRIC"
        }

        try:
            response = self.provider.compute_routes(
                headers=headers,
                body=body,
                timeout=20
            )

            try:
                data = response.json()
            except ValueError:
                data = None

            if response.status_code != 200:
                detalhes = self.extrair_erro_google(data)
                return {
                    "valido": False,
                    "error": self.montar_mensagem_erro_google(detalhes),
                    "status_code": response.status_code,
                    "detalhes": detalhes
                }

            if not isinstance(data, dict):
                return {
                    "valido": False,
                    "error": "Resposta inválida da Google Routes API.",
                    "status_code": response.status_code
                }

            rotas = data.get("routes", [])

            if not isinstance(rotas, list) or not rotas:
                return {
                    "valido": False,
                    "error": "Nenhuma rota encontrada.",
                    "origem": origem,
                    "destino": destino,
                    "dados_google": data
                }

            rotas_com_distancia = [
                rota for rota in rotas
                if (
                    isinstance(rota, dict)
                    and type(rota.get("distanceMeters")) in (int, float)
                )
            ]

            if not rotas_com_distancia:
                return {
                    "valido": False,
                    "error": "Nenhuma rota com distância foi encontrada.",
                    "origem": origem,
                    "destino": destino,
                    "dados_google": data
                }

            menor_rota = min(
                rotas_com_distancia,
                key=lambda rota: rota.get("distanceMeters", float("inf"))
            )

            distancia_metros = menor_rota.get("distanceMeters")
            duracao = menor_rota.get("duration")
            distancia_km = round(distancia_metros / 1000, 2)
            origem_coord = self.extrair_coordenada_rota(menor_rota, "origem")
            destino_coord = self.extrair_coordenada_rota(menor_rota, "destino")

            return {
                "valido": True,
                "descricao": menor_rota.get("description"),
                "distancia_metros": distancia_metros,
                "distancia_km": distancia_km,
                "duracao": duracao,
                "duracao_minutos": self.converter_duracao_para_minutos(duracao),
                "tipo_rota": menor_rota.get("routeLabels"),
                "polyline": self.extrair_polyline(menor_rota),
                "origem_lat": origem_coord.get("lat"),
                "origem_lng": origem_coord.get("lng"),
                "destino_lat": destino_coord.get("lat"),
                "destino_lng": destino_coord.get("lng")
            }

        except requests.exceptions.RequestException as e:
            return {
                "valido": False,
                "error": f"Erro na requisição: {e}"
            }

    def calcular_rota_com_paradas(self, enderecos, otimizar=False):
        return self.calcular_rota_com_destino_fixo(enderecos, otimizar=otimizar)

    def calcular_rota_com_destino_fixo(self, enderecos, otimizar=True):
        validacao = self.validar_enderecos_rota(
            enderecos,
            minimo=2,
            mensagem_minimo="Informe pelo menos origem e destino."
        )

        if not validacao["valido"]:
            return validacao

        enderecos_limpos = validacao["enderecos"]
        resultado = self.calcular_rota_google(
            origem=enderecos_limpos[0],
            destino=enderecos_limpos[-1],
            intermediarios=enderecos_limpos[1:-1],
            otimizar=otimizar
        )

        if not resultado["valido"]:
            return resultado

        resultado["modo_destino"] = "fixo"
        resultado["destino_automatico"] = False
        resultado["indice_destino_escolhido"] = len(enderecos_limpos) - 1
        resultado["indices_ordem_final"] = self.montar_indices_destino_fixo(
            total_enderecos=len(enderecos_limpos),
            ordem_intermediarios=resultado.get("ordem_intermediarios", [])
        )
        return resultado

    def calcular_rota_com_destino_automatico(self, enderecos):
        validacao = self.validar_enderecos_rota(
            enderecos,
            minimo=3,
            mensagem_minimo=(
                "Informe uma origem e pelo menos duas paradas para "
                "usar destino automático."
            )
        )

        if not validacao["valido"]:
            return validacao

        enderecos_limpos = validacao["enderecos"]
        origem = enderecos_limpos[0]
        candidatos = [
            {
                "indice_original": indice,
                "endereco": endereco
            }
            for indice, endereco in enumerate(enderecos_limpos[1:], start=1)
        ]
        melhor_rota = None
        erros = []

        for destino_candidato in candidatos:
            intermediarios = [
                candidato
                for candidato in candidatos
                if candidato["indice_original"] != destino_candidato["indice_original"]
            ]
            resultado = self.calcular_rota_google(
                origem=origem,
                destino=destino_candidato["endereco"],
                intermediarios=[
                    intermediario["endereco"]
                    for intermediario in intermediarios
                ],
                otimizar=True
            )

            if not resultado["valido"]:
                erros.append({
                    "destino": destino_candidato["endereco"],
                    "error": resultado.get("error"),
                    "status_code": resultado.get("status_code")
                })
                continue

            indices_intermediarios = [
                intermediario["indice_original"]
                for intermediario in intermediarios
            ]
            resultado["modo_destino"] = "automatico"
            resultado["destino_automatico"] = True
            resultado["indice_destino_escolhido"] = destino_candidato["indice_original"]
            resultado["indices_ordem_final"] = [
                0,
                *self.ordenar_indices_com_intermediarios(
                    indices_intermediarios,
                    resultado.get("ordem_intermediarios", [])
                ),
                destino_candidato["indice_original"]
            ]

            if melhor_rota is None or self.rota_eh_melhor(resultado, melhor_rota):
                melhor_rota = resultado

        if melhor_rota is None:
            erro = erros[0] if erros else {}
            return {
                "valido": False,
                "error": erro.get("error", "Nenhuma rota automática foi encontrada."),
                "status_code": erro.get("status_code"),
                "rotas_avaliadas": len(candidatos)
            }

        melhor_rota["rotas_avaliadas"] = len(candidatos)
        return melhor_rota

    def calcular_rota_google(self, origem, destino, intermediarios=None, otimizar=False):
        intermediarios = intermediarios or []
        deve_otimizar = bool(intermediarios) and bool(otimizar)
        headers = self.montar_headers_rota_com_paradas()
        body = self.montar_body_rota_com_paradas(
            origem=origem,
            destino=destino,
            intermediarios=intermediarios,
            otimizar=deve_otimizar
        )

        try:
            response = self.provider.compute_routes(
                headers=headers,
                body=body,
                timeout=30
            )

            try:
                data = response.json()
            except ValueError:
                data = None

            if response.status_code != 200:
                detalhes = self.extrair_erro_google(data)
                return {
                    "valido": False,
                    "error": self.montar_mensagem_erro_google(detalhes),
                    "status_code": response.status_code,
                    "detalhes": detalhes
                }

            if not isinstance(data, dict):
                return {
                    "valido": False,
                    "error": "Resposta inválida da Google Routes API.",
                    "status_code": response.status_code
                }

            rotas = data.get("routes", [])

            if not isinstance(rotas, list) or not rotas:
                return {
                    "valido": False,
                    "error": "Nenhum itinerário encontrado.",
                    "dados_google": data
                }

            rotas_com_distancia = [
                rota for rota in rotas
                if (
                    isinstance(rota, dict)
                    and type(rota.get("distanceMeters")) in (int, float)
                )
            ]

            if not rotas_com_distancia:
                return {
                    "valido": False,
                    "error": "Nenhum itinerário com distância foi encontrado.",
                    "dados_google": data
                }

            menor_rota = min(
                rotas_com_distancia,
                key=lambda rota: self.chave_comparacao_rota(rota)
            )
            ordem_intermediarios = menor_rota.get("optimizedIntermediateWaypointIndex")
            enderecos_base = [origem, *intermediarios, destino]
            enderecos_ordenados = self.ordenar_enderecos_com_intermediarios(
                enderecos_base,
                ordem_intermediarios
            )

            return self.montar_resultado_rota(
                rota=menor_rota,
                enderecos_ordenados=enderecos_ordenados,
                ordem_intermediarios=ordem_intermediarios,
                otimizado=deve_otimizar
            )

        except requests.exceptions.RequestException as e:
            return {
                "valido": False,
                "error": f"Erro na requisição: {e}"
            }

    def validar_enderecos_rota(self, enderecos, minimo, mensagem_minimo):
        if not isinstance(enderecos, list) or len(enderecos) < minimo:
            return {
                "valido": False,
                "error": mensagem_minimo
            }

        enderecos_limpos = [
            endereco.strip()
            for endereco in enderecos
            if isinstance(endereco, str) and endereco.strip()
        ]

        if len(enderecos_limpos) != len(enderecos):
            return {
                "valido": False,
                "error": "Todos os pontos precisam ter endereço válido."
            }

        return {
            "valido": True,
            "enderecos": enderecos_limpos
        }

    def montar_headers_rota_com_paradas(self):
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "routes.distanceMeters,"
                "routes.duration,"
                "routes.staticDuration,"
                "routes.description,"
                "routes.routeLabels,"
                "routes.polyline.encodedPolyline,"
                "routes.legs.distanceMeters,"
                "routes.legs.duration,"
                "routes.legs.startLocation,"
                "routes.legs.endLocation,"
                "routes.optimizedIntermediateWaypointIndex"
            )
        }

    def montar_body_rota_com_paradas(
        self,
        origem,
        destino,
        intermediarios,
        otimizar
    ):
        body = {
            "origin": {
                "address": origem
            },
            "destination": {
                "address": destino
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "departureTime": self.horario_atual_google(),
            "computeAlternativeRoutes": False,
            "languageCode": "pt-BR",
            "regionCode": "BR",
            "units": "METRIC"
        }

        if intermediarios:
            body["intermediates"] = [
                {"address": endereco}
                for endereco in intermediarios
            ]
            # A Routes API nao permite otimizar paradas com TRAFFIC_AWARE_OPTIMAL.
            # Usamos TRAFFIC_AWARE + departureTime futuro para equilibrar transito e otimizacao.
            body["optimizeWaypointOrder"] = bool(otimizar)

        return body

    def montar_resultado_rota(
        self,
        rota,
        enderecos_ordenados,
        ordem_intermediarios,
        otimizado
    ):
        totais = self.somar_tempo_distancia_rota(rota)
        distancia_metros = rota.get("distanceMeters")
        duracao = rota.get("duration")
        duracao_segundos = self.converter_duracao_para_segundos(duracao)

        if type(distancia_metros) not in (int, float):
            distancia_metros = totais.get("distancia_metros")

        if type(duracao_segundos) not in (int, float):
            duracao_segundos = totais.get("duracao_segundos")

        return {
            "valido": True,
            "descricao": rota.get("description"),
            "distancia_metros": distancia_metros,
            "distancia_km": self.converter_metros_para_km(distancia_metros),
            "duracao": duracao,
            "duracao_segundos": duracao_segundos,
            "duracao_minutos": self.converter_segundos_para_minutos(duracao_segundos),
            "tipo_rota": rota.get("routeLabels"),
            "polyline": self.extrair_polyline(rota),
            "paradas": self.montar_paradas_da_rota(rota, enderecos_ordenados),
            "trechos": self.montar_trechos_da_rota(rota),
            "ordem_intermediarios": ordem_intermediarios or [],
            "otimizado": bool(otimizado) and isinstance(ordem_intermediarios, list),
            "criterio_rota": "TRAFFIC_AWARE"
        }

    def chave_comparacao_rota(self, rota):
        duracao_segundos = self.converter_duracao_para_segundos(rota.get("duration"))
        distancia_metros = rota.get("distanceMeters")
        totais = self.somar_tempo_distancia_rota(rota)

        if type(duracao_segundos) not in (int, float):
            duracao_segundos = totais.get("duracao_segundos", float("inf"))

        if type(distancia_metros) not in (int, float):
            distancia_metros = totais.get("distancia_metros", float("inf"))

        return duracao_segundos, distancia_metros

    def somar_tempo_distancia_rota(self, rota):
        legs = rota.get("legs", [])

        if not isinstance(legs, list):
            return {
                "duracao_segundos": None,
                "distancia_metros": None
            }

        duracao_total = 0
        distancia_total = 0
        tem_duracao = False
        tem_distancia = False

        for leg in legs:
            if not isinstance(leg, dict):
                continue

            segundos = self.converter_duracao_para_segundos(leg.get("duration"))
            distancia = leg.get("distanceMeters")

            if type(segundos) in (int, float):
                duracao_total += segundos
                tem_duracao = True

            if type(distancia) in (int, float):
                distancia_total += distancia
                tem_distancia = True

        return {
            "duracao_segundos": duracao_total if tem_duracao else None,
            "distancia_metros": distancia_total if tem_distancia else None
        }

    def rota_eh_melhor(self, rota, melhor_rota):
        return self.chave_comparacao_resultado(rota) < self.chave_comparacao_resultado(
            melhor_rota
        )

    def chave_comparacao_resultado(self, rota):
        duracao_segundos = rota.get("duracao_segundos")
        distancia_metros = rota.get("distancia_metros")

        if type(duracao_segundos) not in (int, float):
            duracao_segundos = float("inf")

        if type(distancia_metros) not in (int, float):
            distancia_metros = float("inf")

        return duracao_segundos, distancia_metros

    def converter_duracao_para_minutos(self, duracao):
        return self.converter_segundos_para_minutos(
            self.converter_duracao_para_segundos(duracao)
        )

    def converter_duracao_para_segundos(self, duracao):
        if not isinstance(duracao, str) or not duracao.endswith("s"):
            return None

        try:
            return float(duracao[:-1])
        except ValueError:
            return None

    def converter_segundos_para_minutos(self, segundos):
        if type(segundos) not in (int, float):
            return None

        return round(segundos / 60, 2)

    def converter_metros_para_km(self, distancia_metros):
        if type(distancia_metros) not in (int, float):
            return None

        return round(distancia_metros / 1000, 2)

    def extrair_polyline(self, rota):
        polyline = rota.get("polyline", {})

        if not isinstance(polyline, dict):
            return None

        return polyline.get("encodedPolyline")

    def extrair_coordenada_rota(self, rota, tipo):
        legs = rota.get("legs", [])

        if not isinstance(legs, list) or not legs:
            return {"lat": None, "lng": None}

        leg = legs[0] if tipo == "origem" else legs[-1]
        campo = "startLocation" if tipo == "origem" else "endLocation"

        if not isinstance(leg, dict):
            return {"lat": None, "lng": None}

        location = leg.get(campo, {})
        lat_lng = location.get("latLng", {}) if isinstance(location, dict) else {}

        if not isinstance(lat_lng, dict):
            return {"lat": None, "lng": None}

        return {
            "lat": lat_lng.get("latitude"),
            "lng": lat_lng.get("longitude")
        }

    def ordenar_enderecos_com_intermediarios(self, enderecos, ordem_intermediarios):
        if not ordem_intermediarios:
            return enderecos

        intermediarios = enderecos[1:-1]
        intermediarios_ordenados = [
            intermediarios[indice]
            for indice in ordem_intermediarios
            if isinstance(indice, int) and 0 <= indice < len(intermediarios)
        ]

        if len(intermediarios_ordenados) != len(intermediarios):
            return enderecos

        return [enderecos[0], *intermediarios_ordenados, enderecos[-1]]

    def montar_indices_destino_fixo(self, total_enderecos, ordem_intermediarios):
        indices_intermediarios = list(range(1, total_enderecos - 1))

        return [
            0,
            *self.ordenar_indices_com_intermediarios(
                indices_intermediarios,
                ordem_intermediarios
            ),
            total_enderecos - 1
        ]

    def ordenar_indices_com_intermediarios(self, indices, ordem_intermediarios):
        if not ordem_intermediarios:
            return indices

        indices_ordenados = [
            indices[indice]
            for indice in ordem_intermediarios
            if isinstance(indice, int) and 0 <= indice < len(indices)
        ]

        if len(indices_ordenados) != len(indices):
            return indices

        return indices_ordenados

    def montar_paradas_da_rota(self, rota, enderecos_ordenados):
        legs = rota.get("legs", [])

        if not isinstance(legs, list) or not legs:
            return [
                {
                    "ordem": index + 1,
                    "endereco": endereco,
                    "lat": None,
                    "lng": None
                }
                for index, endereco in enumerate(enderecos_ordenados)
            ]

        coordenadas = []
        primeira_perna = legs[0] if isinstance(legs[0], dict) else {}
        coordenadas.append(self.extrair_lat_lng(primeira_perna.get("startLocation", {})))

        for leg in legs:
            if isinstance(leg, dict):
                coordenadas.append(self.extrair_lat_lng(leg.get("endLocation", {})))

        paradas = []

        for index, endereco in enumerate(enderecos_ordenados):
            coordenada = coordenadas[index] if index < len(coordenadas) else {}
            paradas.append({
                "ordem": index + 1,
                "endereco": endereco,
                "lat": coordenada.get("lat"),
                "lng": coordenada.get("lng")
            })

        return paradas

    def montar_trechos_da_rota(self, rota):
        legs = rota.get("legs", [])

        if not isinstance(legs, list):
            return []

        trechos = []

        for index, leg in enumerate(legs):
            if not isinstance(leg, dict):
                continue

            distancia_metros = leg.get("distanceMeters")
            duracao = leg.get("duration")
            trechos.append({
                "ordem": index + 1,
                "distancia_metros": distancia_metros,
                "distancia_km": (
                    round(distancia_metros / 1000, 2)
                    if type(distancia_metros) in (int, float)
                    else None
                ),
                "duracao": duracao,
                "duracao_minutos": self.converter_duracao_para_minutos(duracao)
            })

        return trechos

    def extrair_lat_lng(self, location):
        lat_lng = location.get("latLng", {}) if isinstance(location, dict) else {}

        if not isinstance(lat_lng, dict):
            return {"lat": None, "lng": None}

        return {
            "lat": lat_lng.get("latitude"),
            "lng": lat_lng.get("longitude")
        }

    def horario_atual_google(self):
        # A Routes API rejeita timestamps no instante atual; uma pequena margem
        # futura mantem a consulta praticamente em tempo real sem dar erro.
        horario_saida = datetime.now(timezone.utc) + timedelta(minutes=2)
        return horario_saida.isoformat().replace("+00:00", "Z")

    def extrair_erro_google(self, data):
        if not isinstance(data, dict):
            return None

        erro = data.get("error")

        if not isinstance(erro, dict):
            return None

        partes = []

        mensagem = erro.get("message")
        status = erro.get("status")

        if mensagem:
            partes.append(str(mensagem))

        if status and status not in partes:
            partes.append(str(status))

        for detalhe in erro.get("details", [])[:2]:
            if not isinstance(detalhe, dict):
                continue

            motivo = detalhe.get("reason")
            dominio = detalhe.get("domain")

            if motivo:
                partes.append(str(motivo))

            if dominio:
                partes.append(str(dominio))

        return " | ".join(partes) if partes else None

    def montar_mensagem_erro_google(self, detalhes):
        if detalhes:
            return f"Erro ao consultar Google Routes API: {detalhes}"

        return "Erro ao consultar Google Routes API."
