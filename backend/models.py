
from pydantic import BaseModel, Field


class TestRecord(BaseModel):
    id: str
    investigation: str
    investigation_id: str | None = None
    material: str | None = None
    oxygen_pct: float | None = None
    oxygen_context: str | None = None
    pressure_psi: float | None = None
    airflow: str | None = None
    result: str | None = None
    conditions: dict[str, str | float | int | None] = Field(default_factory=dict)
    source_url: str | None = None

class Habitat(BaseModel):
    name: str
    oxygen_pct: float
    pressure_psi: float
    status: str | None = None
    source_url: str | None = None
    note: str | None = None

class RankRequest(BaseModel):
    habitat: str   # a habitat name, e.g. "Moon base"