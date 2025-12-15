"""
Binah-Σ Engine v2.0 - Enhanced with:
- Multi-provider LLM support
- Transparent scoring
- Quality validation
- Provider failover
"""

import json
import os
import logging
from typing import Dict
from dotenv import load_dotenv

from llm_providers import LLMOrchestrator
from scoring_engine import ScoringEngine, DecisionDimensions
from quality_validator import QualityValidator
from schemas import BinahSigmaResponse

load_dotenv()

# Logger
logger = logging.getLogger("binah_sigma")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Initialize components
llm_orchestrator = LLMOrchestrator(primary_provider="mistral")
scoring_engine = ScoringEngine(industry="general")


BINAH_SIGMA_SYSTEM = """
You are Binah-Σ, a deep synthesis reasoning engine for evaluating complex decisions.

CRITICAL: You must output ONLY valid JSON. No additional text, no markdown, no explanations outside the JSON.

Your role is to analyze decisions across multiple dimensions:

1. **Clarity** (0-100): How well-defined is the problem?
2. **Stakeholder Benefit** (0-100): Net benefit across all affected parties
3. **Feasibility** (0-100): Likelihood of successful implementation
4. **Ethical Risk**: Categorical assessment of ethical concerns

REQUIRED OUTPUT SCHEMA:

{
  "dimensions": {
    "clarity_score": <int 0-100>,
    "stakeholder_benefit_score": <int 0-100>,
    "feasibility_score": <int 0-100>,
    "ethical_risk_level": "<None|Low|Medium|High|Critical>"
  },
  "ethical_alignment": "<Aligned|Partial|Misaligned>",
  "systemic_risk": "<Low|Medium|High|Critical>",
  "key_tensions": [
    "<tension 1: describe structural trade-off>",
    "<tension 2: ...>",
    "<tension 3: ...>",
    "<tension 4: ...>"
  ],
  "unintended_consequences": [
    "<consequence 1: describe second-order effect>",
    "<consequence 2: ...>",
    "<consequence 3: ...>",
    "<consequence 4: ...>",
    "<consequence 5: ...>"
  ],
  "binah_recommendation": "<Concrete, actionable recommendation (50+ chars)>",
  "explanation_summary": "<Clear explanation of the analysis rationale (100+ chars)>",
  "analysis_version": "v2.0"
}

CRITICAL QUALITY REQUIREMENTS:
- key_tensions: MINIMUM 4 items, each substantive (10+ chars)
- unintended_consequences: MINIMUM 5 items, each substantive (10+ chars)
- binah_recommendation: MINIMUM 50 characters, specific and actionable
- explanation_summary: MINIMUM 100 characters, clear rationale
- NO generic phrases like "it depends", "consider all options", "evaluate carefully"
- NO placeholder text like "N/A", "TBD", "None"
- Each tension and consequence must be unique and specific

ANALYSIS APPROACH:
1. Decompose the decision into constituent elements (Binah)
2. Analyze ethical implications and stakeholder impacts
3. Identify systemic risks and structural tensions
4. Synthesize coherence across all dimensions (Σ)
5. Generate structured, measurable evaluation

DO NOT generate binah_sigma_index, binah_sigma_confidence, or decision_coherence.
These will be calculated deterministically from your dimensional scores.
"""


BINAH_SIGMA_PROMPT = """
DECISION ANALYSIS REQUEST:

Context: {context}

Decision Question: {decision_question}

Stakeholders: {stakeholders}

Constraints: {constraints}

Time Horizon: {time_horizon}

Apply the Binah-Σ methodology to evaluate this decision.
Return ONLY valid JSON following the schema above.
"""


async def run_binah_sigma(
    data: Dict,
    provider: str = None,
    industry: str = "general"
) -> Dict:
    """
    Execute Binah-Σ analysis with enhanced v2 architecture.

    Args:
        data: Decision context dict
        provider: Specific LLM provider to use (optional)
        industry: Industry for scoring weights

    Returns:
        Validated BinahSigmaResponse as dict

    Raises:
        ValueError: If quality validation fails
        RuntimeError: If all LLM providers fail
    """
    prompt = BINAH_SIGMA_PROMPT.format(**data)

    messages = [
        {"role": "system", "content": BINAH_SIGMA_SYSTEM},
        {"role": "user", "content": prompt}
    ]

    try:
        # Step 1: Get LLM evaluation
        logger.info("Requesting LLM analysis...")
        raw_content, provider_used = await llm_orchestrator.complete(
            messages=messages,
            temperature=0.2,
            provider=provider
        )

        logger.info(f"LLM response received from {provider_used}")

        # Step 2: Parse JSON
        parsed = json.loads(raw_content)

        # Step 3: Extract dimensions
        if "dimensions" not in parsed:
            raise ValueError("LLM output missing 'dimensions' field")

        dimensions = DecisionDimensions(**parsed["dimensions"])

        # Step 4: Calculate index deterministically
        scorer = ScoringEngine(industry=industry)
        calculated_index = scorer.calculate_index(dimensions)
        calculated_confidence = scorer.derive_confidence(dimensions)
        calculated_coherence = scorer.derive_coherence(calculated_index)

        logger.info(
            f"Calculated index={calculated_index:.2f}, "
            f"confidence={calculated_confidence:.2f}, "
            f"coherence={calculated_coherence}"
        )

        # Step 5: Build final response
        final_response = {
            "binah_sigma_index": calculated_index,
            "binah_sigma_confidence": calculated_confidence,
            "decision_coherence": calculated_coherence,
            "dimensions": dimensions.dict(),
            "ethical_alignment": parsed.get("ethical_alignment", "Unknown"),
            "systemic_risk": parsed.get("systemic_risk", "Unknown"),
            "key_tensions": parsed.get("key_tensions", []),
            "unintended_consequences": parsed.get("unintended_consequences", []),
            "binah_recommendation": parsed.get("binah_recommendation", ""),
            "explanation_summary": parsed.get("explanation_summary", ""),
            "analysis_version": parsed.get("analysis_version", "v2.0"),
            "metadata": {
                "provider_used": provider_used,
                "industry": industry,
                "scoring_breakdown": scorer.get_breakdown(dimensions)
            }
        }

        # Step 6: Validate schema
        validated = BinahSigmaResponse(**final_response)

        # Step 7: Quality validation
        try:
            QualityValidator.validate(validated)
            quality_score = QualityValidator.get_quality_score(validated)
            logger.info(f"Quality validation passed (score: {quality_score:.1f}/100)")

            final_response["metadata"]["quality_score"] = quality_score

        except ValueError as ve:
            logger.warning(f"Quality validation failed: {ve}")
            # Option: Re-try with different provider or stronger prompt
            # For now, we raise the error
            raise

        logger.info(
            f"BINAH-Σ ANALYSIS COMPLETE | "
            f"index={calculated_index:.2f} | "
            f"confidence={calculated_confidence:.2f} | "
            f"provider={provider_used}"
        )

        return final_response

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON output: {e}")
        logger.error(f"Raw content: {raw_content[:500]}...")
        raise ValueError(f"LLM returned invalid JSON: {e}")

    except Exception as e:
        logger.exception("BINAH-Σ ENGINE FAILURE")
        raise


def get_provider_stats() -> dict:
    """Get statistics for all LLM providers"""
    return llm_orchestrator.get_stats()


def switch_provider(provider: str):
    """
    Switch primary LLM provider.

    Args:
        provider: "mistral", "gemini", or "deepseek"
    """
    llm_orchestrator.set_primary_provider(provider)
    logger.info(f"Switched primary provider to: {provider}")
