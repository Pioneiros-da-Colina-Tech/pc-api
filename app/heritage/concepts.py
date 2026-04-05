from enum import StrEnum


class RequestStatusConcept(StrEnum):
    PENDING = "pendente"
    APPROVED = "aprovado"
    REJECTED = "reprovado"
    DELIVERED = "entregue"
    RETURNED = "devolvido"
