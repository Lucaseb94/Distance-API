import requests
import re


class BuscaCEP:
    def limpar_cep(self, cep):
        """
        Remove tudo que não for número.
        Exemplo: 07190-100 -> 07190100
        """
        if not cep:
            return None

        return re.sub(r"\D", "", str(cep))

    def validar_cep(self, cep):
        """
        Valida se o CEP tem exatamente 8 números.
        """
        cep_limpo = self.limpar_cep(cep)

        if not cep_limpo:
            return {
                "valido": False,
                "error": "CEP é obrigatório."
            }

        if len(cep_limpo) != 8:
            return {
                "valido": False,
                "error": "CEP inválido. O CEP deve conter 8 números."
            }

        return {
            "valido": True,
            "cep_limpo": cep_limpo,
            "cep_formatado": self.formatar_cep(cep_limpo)
        }

    def formatar_cep(self, cep):
        """
        Formata o CEP no padrão 00000-000.
        """
        cep_limpo = self.limpar_cep(cep)

        if not cep_limpo or len(cep_limpo) != 8:
            return None

        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"

    def buscar_endereco(self, cep, numero=None):
        validacao = self.validar_cep(cep)

        if not validacao["valido"]:
            return {
                "valido": False,
                "error": validacao["error"]
            }

        cep_limpo = validacao["cep_limpo"]

        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict):
                return {
                    "valido": False,
                    "error": "Resposta inválida do ViaCEP."
                }

            if "erro" in data:
                if self.deve_tentar_cep_generico(cep_limpo):
                    return self.montar_resposta_cep_generico(
                        cep,
                        cep_limpo,
                        validacao["cep_formatado"],
                        data
                    )

                return {
                    "valido": False,
                    "cep_digitado": cep,
                    "cep_limpo": cep_limpo,
                    "cep_formatado": validacao["cep_formatado"],
                    "error": "CEP não encontrado."
                }

            endereco_formatado = self.montar_endereco_completo(data, numero)

            return {
                "valido": True,
                "cep_digitado": cep,
                "cep_limpo": cep_limpo,
                "cep_formatado": validacao["cep_formatado"],
                "logradouro": data.get("logradouro"),
                "numero": numero,
                "complemento": data.get("complemento"),
                "bairro": data.get("bairro"),
                "cidade": data.get("localidade"),
                "uf": data.get("uf"),
                "estado": data.get("estado"),
                "regiao": data.get("regiao"),
                "ibge": data.get("ibge"),
                "ddd": data.get("ddd"),
                "endereco_completo": endereco_formatado,
                "endereco_google": endereco_formatado,
                "dados_viacep": data
            }

        except ValueError:
            return {
                "valido": False,
                "error": "Resposta inválida do ViaCEP."
            }
        except requests.exceptions.RequestException as e:
            return {
                "valido": False,
                "error": f"Erro na requisição: {e}"
            }

    def montar_endereco_completo(self, data, numero=None):
        """
        Monta o endereço em um formato melhor para usar no Google Geocoding.
        Exemplo:
        Rodovia Hélio Smidt, 100, Aeroporto, Guarulhos, SP, 07190-100, Brasil
        """

        partes = []

        logradouro = data.get("logradouro")
        bairro = data.get("bairro")
        cidade = data.get("localidade")
        uf = data.get("uf")
        cep = data.get("cep")

        if logradouro:
            if numero:
                partes.append(f"{logradouro}, {numero}")
            else:
                partes.append(logradouro)

        if bairro:
            partes.append(bairro)

        if cidade:
            partes.append(cidade)

        if uf:
            partes.append(uf)

        if cep:
            partes.append(cep)

        partes.append("Brasil")

        return ", ".join(partes)

    def deve_tentar_cep_generico(self, cep_limpo):
        return isinstance(cep_limpo, str) and cep_limpo.endswith("000")

    def montar_resposta_cep_generico(
        self,
        cep_digitado,
        cep_limpo,
        cep_formatado,
        dados_viacep
    ):
        endereco_formatado = f"{cep_formatado}, Brasil"

        return {
            "valido": True,
            "cep_digitado": cep_digitado,
            "cep_limpo": cep_limpo,
            "cep_formatado": cep_formatado,
            "logradouro": None,
            "numero": None,
            "complemento": None,
            "bairro": None,
            "cidade": None,
            "uf": None,
            "estado": None,
            "regiao": None,
            "ibge": None,
            "ddd": None,
            "endereco_completo": endereco_formatado,
            "endereco_google": endereco_formatado,
            "dados_viacep": dados_viacep,
            "fonte_endereco": "cep_generico"
        }

    def incluir_numero(self, endereco, numero):
        if not endereco:
            return {"error": "Endereço é obrigatório."}

        if not numero:
            return {"error": "Número é obrigatório."}

        return {
            "endereco_completo": f"{endereco}, {numero}"
        }


Busca_CEP = BuscaCEP
