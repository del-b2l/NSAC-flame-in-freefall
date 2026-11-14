from pydantic import BaseModel, Field
from typing import Optional, Union

class TestRecord(BaseModel):
    id: str
    investigation: str
    investigation_id: Optional[str] = None
    material: Optional[str] = None
    oxygen_pct: Optional[float] = None
    pressure_psi: Optional[float] = None
    airflow: Optional[str] = None
    result: Optional[str] = None
    conditions: dict[str, Union[str, float, int, None]] = Field(default_factory=dict)
    source_url: Optional[str] = None

class Habitat(BaseModel):
    name: str
    oxygen_pct: float
    pressure_psi: float
    status: Optional[str] = None
    source_url: Optional[str] = None
    note: Optional[str] = None

class RankRequest(BaseModel):
    habitat: str   # a habitat name, e.g. "Moon base"