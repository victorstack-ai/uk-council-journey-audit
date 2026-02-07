from pydantic import BaseModel
from typing import List, Optional

class JourneyStep(BaseModel):
    name: str
    action: str  # e.g., "search", "click", "navigate"
    target: Optional[str] = None

class Journey(BaseModel):
    name: str
    description: str
    steps: List[JourneyStep]

class AuditResult(BaseModel):
    journey_name: str
    url: str
    success: bool
    steps_taken: int
    duration: float
    error_message: Optional[str] = None
    log: List[str]
