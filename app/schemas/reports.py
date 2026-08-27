"""Security Reports schema definitions (Phase 5 placeholder contract)."""
from pydantic import BaseModel, Field
from typing import Any, Dict, List

class ReportCreateRequest(BaseModel):
    target: str
    tool: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
