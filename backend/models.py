from pydantic import BaseModel
from typing import Optional

class TestRecord(BaseModel):
    id: str
    investigation: str            # e.g. "Saffire-VI", "BASS-II"
    material: Optional[str] = None
    oxygen_pct: Optional[float] = None
    pressure_psi: Optional[float] = None
    airflow: Optional[str] = None
    result: Optional[str] = None
    source_url: Optional[str] = None

class Habitat(BaseModel):
    name: str
    oxygen_pct: float
    pressure_psi: float