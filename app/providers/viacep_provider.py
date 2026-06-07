from app.providers.cep_provider import BuscaCEP


class ViaCepProvider:
    def __init__(self):
        self.client = BuscaCEP()

    def find_address(self, cep, numero=None):
        return self.client.buscar_endereco(cep, numero=numero)
