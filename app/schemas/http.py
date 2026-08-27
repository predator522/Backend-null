"""HTTP Analysis schema definitions (Phase 4 placeholder contract)."""
from pydantic import BaseModel, Field

class HTTPAnalyzeRequest(BaseModel):
    url: str = Field(..., description="Public HTTP/HTTPS URL")
