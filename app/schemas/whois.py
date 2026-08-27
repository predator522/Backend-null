"""WHOIS schema definitions (Phase 3 placeholder contract)."""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class WhoisLookupRequest(BaseModel):
    domain: str = Field(..., description="Target domain for WHOIS lookup")
