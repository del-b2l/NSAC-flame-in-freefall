from fastapi import APIRouter

from backend.data_loader import read_processed

router = APIRouter()


@router.get("/earth-use")
def earth_use():
    research = [
        {
            "investigation_id": inv.get("id"),
            "investigation_name": inv.get("name"),
            "benefits": inv["earth_benefits"],
            "source_url": inv.get("landing_url"),
        }
        for inv in read_processed("investigations.json", [])
        if inv.get("earth_benefits")
    ]
    return {"spinoffs": read_processed("earth_use.json", []), "from_research": research}