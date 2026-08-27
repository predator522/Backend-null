"""CVE Lookup schema definitions (Phase 5 placeholder contract)."""
from pydantic import BaseModel, Field

class CVEResponse(BaseModel):
    id: str
    description: str
