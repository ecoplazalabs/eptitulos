import re
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, field_validator

VALID_OFICINAS = {
    "LIMA",
    "AREQUIPA",
    "TRUJILLO",
    "CHICLAYO",
    "CUSCO",
    "HUANCAYO",
    "PIURA",
    "IQUITOS",
    "TACNA",
    "ICA",
    "PUNO",
    "AYACUCHO",
    "JUNIN",
    "LAMBAYEQUE",
    "ANCASH",
    "CAJAMARCA",
    "LORETO",
    "UCAYALI",
    "SAN_MARTIN",
    "TUMBES",
    "MOQUEGUA",
    "MADRE_DE_DIOS",
    "HUANUCO",
    "PASCO",
    "APURIMAC",
    "AMAZONAS",
    "HUANCAVELICA",
}

AnalysisStatus = Literal["pending", "processing", "completed", "failed"]


class Carga(BaseModel):
    tipo: str
    detalle: str
    vigente: bool
    fecha: str | None = None


class CreateAnalysisRequest(BaseModel):
    oficina: str
    partida: str
    area_registral: str = "Propiedad Inmueble Predial"

    @field_validator("oficina")
    @classmethod
    def validate_oficina(cls, v: str) -> str:
        normalized = v.upper().strip()
        if normalized not in VALID_OFICINAS:
            raise ValueError(
                f"Invalid oficina '{v}'. Must be one of: {sorted(VALID_OFICINAS)}"
            )
        return normalized

    @field_validator("partida")
    @classmethod
    def validate_partida(cls, v: str) -> str:
        cleaned = v.strip()
        if not re.match(r"^\d{6,12}$", cleaned):
            raise ValueError(
                "Partida must contain only digits and be between 6 and 12 characters long"
            )
        return cleaned

    @field_validator("area_registral")
    @classmethod
    def validate_area_registral(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("area_registral cannot be empty")
        if len(cleaned) > 200:
            raise ValueError("area_registral is too long (max 200 characters)")
        return cleaned


class AnalysisCreatedResponse(BaseModel):
    id: UUID
    status: AnalysisStatus
    oficina: str
    partida: str
    created_at: datetime


class AnalysisSummaryResponse(BaseModel):
    id: UUID
    oficina: str
    partida: str
    status: AnalysisStatus
    total_asientos: int | None = None
    cargas_count: int
    duration_seconds: int | None = None
    created_at: datetime
    completed_at: datetime | None = None


class AnalysisDetailResponse(BaseModel):
    id: UUID
    oficina: str
    partida: str
    area_registral: str
    status: AnalysisStatus
    total_asientos: int | None = None
    informe: str | None = None
    cargas_encontradas: list[Carga]
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = None
    claude_cost_usd: Decimal | None = None
    created_at: datetime


# PdfUrlResponse removed - PDF is served directly via GET /analyses/{id}/pdf
