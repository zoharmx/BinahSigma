from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class BinahSigmaRequest(BaseModel):
    context: str
    decision_question: str
    stakeholders: List[str]
    constraints: List[str]
    time_horizon: str

    # Optional parameters for v2
    provider: Optional[str] = Field(None, description="Specific LLM provider to use")
    industry: Optional[str] = Field("general", description="Industry for scoring configuration")


class BinahSigmaResponse(BaseModel):
    binah_sigma_index: float
    binah_sigma_confidence: float
    decision_coherence: str
    ethical_alignment: str
    systemic_risk: str
    key_tensions: List[str]
    unintended_consequences: List[str]
    binah_recommendation: str
    explanation_summary: str
    analysis_version: str

    # Optional fields for v2 (backward compatible)
    dimensions: Optional[Dict[str, Any]] = Field(None, description="Dimensional breakdown")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Analysis metadata")
