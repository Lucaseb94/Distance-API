from dataclasses import dataclass

from app.core.exceptions import ValidationError


@dataclass
class SimpleRouteRequest:
    cep_origem: str
    numero_origem: str
    cep_destino: str
    numero_destino: str

    @classmethod
    def from_payload(cls, payload):
        data = cls(
            cep_origem=str(payload.get("cep_origem", "")).strip(),
            numero_origem=str(payload.get("numero_origem", "")).strip(),
            cep_destino=str(payload.get("cep_destino", "")).strip(),
            numero_destino=str(payload.get("numero_destino", "")).strip()
        )
        data.validate()
        return data

    def validate(self):
        campos_obrigatorios = {
            "cep_origem": (self.cep_origem, "CEP de origem é obrigatório."),
            "numero_origem": (self.numero_origem, "Número da origem é obrigatório."),
            "cep_destino": (self.cep_destino, "CEP de destino é obrigatório."),
            "numero_destino": (self.numero_destino, "Número do destino é obrigatório."),
        }

        for _, (valor, mensagem) in campos_obrigatorios.items():
            if not valor:
                raise ValidationError(mensagem)

    def to_legacy_payload(self):
        return {
            "cep_origem": self.cep_origem,
            "numero_origem": self.numero_origem,
            "cep_destino": self.cep_destino,
            "numero_destino": self.numero_destino
        }
