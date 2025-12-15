"""
Transparent Scoring Engine for Binah-Σ

Separates LLM evaluation from index calculation, providing:
- Auditable scoring algorithm
- Configurable weights
- Ethical veto mechanisms
- Industry-specific tuning
"""

from typing import Literal
from pydantic import BaseModel, Field


class DecisionDimensions(BaseModel):
    """Granular dimensions evaluated by LLM"""

    clarity_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="How well-defined is the problem and context (0-100)"
    )
    stakeholder_benefit_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Net benefit for all stakeholders (0-100)"
    )
    feasibility_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Probability of successful implementation (0-100)"
    )
    ethical_risk_level: Literal["None", "Low", "Medium", "High", "Critical"] = Field(
        ...,
        description="Detected ethical risk level"
    )


class ScoringEngine:
    """Deterministic index calculation from LLM dimensions"""

    # Industry-specific weight configurations
    INDUSTRY_WEIGHTS = {
        "general": {
            "clarity": 0.20,
            "stakeholder": 0.30,
            "feasibility": 0.30,
            "ethics": 0.20
        },
        "healthcare": {
            "clarity": 0.15,
            "stakeholder": 0.25,
            "feasibility": 0.20,
            "ethics": 0.40  # Higher ethical weight
        },
        "finance": {
            "clarity": 0.25,
            "stakeholder": 0.25,
            "feasibility": 0.35,
            "ethics": 0.15
        },
        "nonprofit": {
            "clarity": 0.15,
            "stakeholder": 0.40,  # Stakeholder focus
            "feasibility": 0.15,
            "ethics": 0.30
        },
        "technology": {
            "clarity": 0.25,
            "stakeholder": 0.25,
            "feasibility": 0.35,
            "ethics": 0.15
        }
    }

    def __init__(self, industry: str = "general"):
        """
        Initialize scoring engine with industry-specific configuration.

        Args:
            industry: Industry type for weight configuration
        """
        self.industry = industry
        self.weights = self.INDUSTRY_WEIGHTS.get(industry, self.INDUSTRY_WEIGHTS["general"])

        # Ethical risk penalties (converts categorical to numerical)
        self.ethical_penalties = {
            "None": 1.0,      # 100% of score
            "Low": 0.9,       # 90% of score
            "Medium": 0.6,    # 60% of score
            "High": 0.3,      # 30% of score (severe penalty)
            "Critical": 0.0   # 0% of score (nullifies ethical component)
        }

        # Ethical veto caps (prevents dangerous decisions from scoring high)
        self.ethical_caps = {
            "Critical": 0.40,  # Never exceed 0.40 regardless of other scores
            "High": 0.60       # Never exceed 0.60
        }

    def calculate_index(self, dimensions: DecisionDimensions) -> float:
        """
        Calculate Binah-Σ Index from dimensions using transparent algorithm.

        Formula:
            raw_index = Σ(normalized_score_i × weight_i)
            final_index = min(raw_index, ethical_cap)

        Args:
            dimensions: DecisionDimensions from LLM evaluation

        Returns:
            float: Index between 0.0 and 1.0
        """
        # Step 1: Normalize scores from 0-100 to 0.0-1.0
        s_clarity = dimensions.clarity_score / 100.0
        s_benefit = dimensions.stakeholder_benefit_score / 100.0
        s_feasibility = dimensions.feasibility_score / 100.0

        # Step 2: Convert ethical risk category to numerical score
        risk_level = dimensions.ethical_risk_level
        s_ethics = self.ethical_penalties[risk_level]

        # Step 3: Calculate weighted average
        raw_index = (
            (s_clarity * self.weights["clarity"]) +
            (s_benefit * self.weights["stakeholder"]) +
            (s_feasibility * self.weights["feasibility"]) +
            (s_ethics * self.weights["ethics"])
        )

        # Step 4: Apply ethical veto (safety guardrail)
        if risk_level in self.ethical_caps:
            raw_index = min(raw_index, self.ethical_caps[risk_level])

        return round(raw_index, 2)

    def derive_coherence(self, index: float) -> str:
        """
        Derive coherence level from index.

        Args:
            index: Binah-Σ Index (0.0-1.0)

        Returns:
            str: "Low" | "Medium" | "High"
        """
        if index >= 0.75:
            return "High"
        elif index >= 0.5:
            return "Medium"
        else:
            return "Low"

    def derive_confidence(self, dimensions: DecisionDimensions) -> float:
        """
        Calculate confidence based on dimension variance.

        Logic: Lower variance across dimensions = higher confidence
        If all scores agree (all high or all low), confidence is high.

        Args:
            dimensions: DecisionDimensions from LLM

        Returns:
            float: Confidence score (0.0-1.0)
        """
        scores = [
            dimensions.clarity_score,
            dimensions.stakeholder_benefit_score,
            dimensions.feasibility_score
        ]

        # Calculate range (variance proxy)
        score_range = max(scores) - min(scores)

        # Convert to confidence (inverse relationship)
        # Range 0 → confidence 1.0, Range 100 → confidence 0.0
        confidence = 1.0 - (score_range / 100.0)

        # Apply floor (minimum confidence)
        confidence = max(0.5, confidence)

        return round(confidence, 2)

    def get_breakdown(self, dimensions: DecisionDimensions) -> dict:
        """
        Get detailed breakdown of how index was calculated.

        Args:
            dimensions: DecisionDimensions from LLM

        Returns:
            dict: Breakdown showing contribution of each dimension
        """
        s_clarity = dimensions.clarity_score / 100.0
        s_benefit = dimensions.stakeholder_benefit_score / 100.0
        s_feasibility = dimensions.feasibility_score / 100.0
        risk_level = dimensions.ethical_risk_level
        s_ethics = self.ethical_penalties[risk_level]

        return {
            "components": {
                "clarity": {
                    "score": dimensions.clarity_score,
                    "normalized": s_clarity,
                    "weight": self.weights["clarity"],
                    "contribution": round(s_clarity * self.weights["clarity"], 3)
                },
                "stakeholder_benefit": {
                    "score": dimensions.stakeholder_benefit_score,
                    "normalized": s_benefit,
                    "weight": self.weights["stakeholder"],
                    "contribution": round(s_benefit * self.weights["stakeholder"], 3)
                },
                "feasibility": {
                    "score": dimensions.feasibility_score,
                    "normalized": s_feasibility,
                    "weight": self.weights["feasibility"],
                    "contribution": round(s_feasibility * self.weights["feasibility"], 3)
                },
                "ethics": {
                    "risk_level": risk_level,
                    "penalty_multiplier": s_ethics,
                    "weight": self.weights["ethics"],
                    "contribution": round(s_ethics * self.weights["ethics"], 3)
                }
            },
            "raw_index": self.calculate_index(dimensions),
            "ethical_cap_applied": risk_level in self.ethical_caps,
            "final_index": self.calculate_index(dimensions),
            "industry": self.industry
        }
