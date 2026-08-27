"""IP Intelligence schema definitions (Phase 3 placeholder contract)."""
from pydantic import BaseModel, Field

class IPAnalyzeRequest(BaseModel):
    ip: str = Field(..., description="Public IPv4 or IPv6 target")
