from dataclasses import dataclass

from app.core.exceptions import ValidationError


def normalize_email(email):
    return str(email).strip().lower()


@dataclass
class RegisterRequest:
    nome: str
    email: str
    senha: str
    confirmar_senha: str

    @classmethod
    def from_payload(cls, payload):
        data = cls(
            nome=str(payload.get("nome", "")).strip(),
            email=normalize_email(payload.get("email", "")),
            senha=str(payload.get("senha", "")),
            confirmar_senha=str(payload.get("confirmar_senha", ""))
        )
        data.validate()
        return data

    def validate(self):
        if not self.nome:
            raise ValidationError("Nome é obrigatório.")

        if not self.email:
            raise ValidationError("E-mail é obrigatório.")

        if len(self.senha) < 6:
            raise ValidationError("A senha deve ter pelo menos 6 caracteres.")

        if self.senha != self.confirmar_senha:
            raise ValidationError("As senhas precisam ser iguais.")


@dataclass
class LoginRequest:
    email: str
    senha: str

    @classmethod
    def from_payload(cls, payload):
        data = cls(
            email=normalize_email(payload.get("email", "")),
            senha=str(payload.get("senha", ""))
        )
        data.validate()
        return data

    def validate(self):
        if not self.email:
            raise ValidationError("E-mail é obrigatório.")

        if not self.senha:
            raise ValidationError("Senha é obrigatória.")
