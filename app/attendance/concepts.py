from enum import StrEnum


class AttendanceStatus(StrEnum):
    PRESENTE = "presente"
    AUSENTE = "ausente"
    JUSTIFICADO = "justificado"
