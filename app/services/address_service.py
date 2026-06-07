from app.core.exceptions import ValidationError
from app.providers.viacep_provider import ViaCepProvider


class AddressService:
    def __init__(self, provider=None):
        self.provider = provider or ViaCepProvider()

    def resolve(self, cep, numero=None, label="Endereço"):
        endereco = self.provider.find_address(cep, numero=numero)

        if not endereco.get("valido"):
            raise ValidationError(f"{label}: {endereco.get('error')}")

        return endereco

    def resolve_stop(self, stop, index):
        try:
            return self.resolve(stop.cep, numero=stop.numero, label=f"Ponto {index + 1}")
        except ValidationError:
            raise
