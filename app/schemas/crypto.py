"""Cryptography Utilities schema definitions (Phase 3 placeholder contract)."""
from pydantic import BaseModel, Field

class HashRequest(BaseModel):
    input_text: str = Field(...)
    algorithm: str = Field(default="sha256")
