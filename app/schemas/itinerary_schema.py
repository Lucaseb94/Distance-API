from dataclasses import dataclass

from app.core.exceptions import ValidationError


MAX_ITINERARY_POINTS = 27


def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_destination_mode(mode):
    normalized = str(mode or "fixo").strip().lower()

    if normalized in ("automatico", "auto", "destino_automatico", "melhor_final"):
        return "automatico"

    return "fixo"


@dataclass
class StopRequest:
    cep: str
    numero: str

    @classmethod
    def from_payload(cls, payload, index):
        if not isinstance(payload, dict):
            raise ValidationError(f"Ponto {index + 1}: dados inválidos.")

        data = cls(
            cep=clean_text(payload.get("cep")),
            numero=clean_text(payload.get("numero"))
        )
        data.validate(index)
        return data

    def validate(self, index):
        if not self.cep:
            raise ValidationError(f"Ponto {index + 1}: CEP é obrigatório.")


@dataclass
class ItineraryRequest:
    paradas: list
    modo_destino: str

    @classmethod
    def from_payload(cls, payload):
        paradas_payload = payload.get("paradas", [])
        modo_destino = normalize_destination_mode(payload.get("modo_destino"))

        if not isinstance(paradas_payload, list) or len(paradas_payload) < 2:
            raise ValidationError("Informe pelo menos origem e destino.")

        if modo_destino == "automatico" and len(paradas_payload) < 3:
            raise ValidationError(
                "No destino automático, informe uma origem e pelo menos "
                "duas paradas candidatas."
            )

        if len(paradas_payload) > MAX_ITINERARY_POINTS:
            raise ValidationError(
                f"Informe no máximo {MAX_ITINERARY_POINTS} pontos por itinerário."
            )

        paradas = [
            StopRequest.from_payload(parada, index)
            for index, parada in enumerate(paradas_payload)
        ]

        return cls(paradas=paradas, modo_destino=modo_destino)
