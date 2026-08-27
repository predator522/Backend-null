"""TLS Inspector schema definitions (Phase 3 placeholder contract)."""
from pydantic import BaseModel, Field

class TLSInspectRequest(BaseModel):
    host: str = Field(..., description="Public domain or hostname")
    port: int = Field(default=443)
