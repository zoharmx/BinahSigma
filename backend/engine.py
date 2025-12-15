import json
import os
import logging
import asyncio
from pydantic import ValidationError
from dotenv import load_dotenv
from mistralai import Mistral
from schemas import BinahSigmaResponse

# Load environment variables
load_dotenv()

# Logger estructurado
logger = logging.getLogger("binah_sigma")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Cliente síncrono - usaremos loop.run_in_executor para async
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

BINAH_SIGMA_SYSTEM = """
You are Binah-Σ, a deep synthesis reasoning engine.
Your role is NOT to chat, speculate, persuade, or generate generic advice.

STRICT RULES:
- Decompose complexity (Binah) and synthesize coherence (Σ).
- Analyze decisions across ethical, systemic, and structural dimensions.
- Never expose chain-of-thought or internal reasoning.
- Output ONLY valid JSON following the Binah-Σ schema exactly.
- Do not add commentary, explanations, or text outside the JSON structure.

Your output must include:
- binah_sigma_index: float between 0 and 1 (decision quality score)
- binah_sigma_confidence: float between 0 and 1 (confidence in analysis)
- decision_coherence: string (Low/Medium/High)
- ethical_alignment: string (Aligned/Partial/Misaligned)
- systemic_risk: string (Low/Medium/High/Critical)
- key_tensions: array of strings (main conflicts/trade-offs)
- unintended_consequences: array of strings (potential second-order effects)
- binah_recommendation: string (synthesized recommendation)
- explanation_summary: string (brief explanation of the analysis)
- analysis_version: string (always "v1.0" for now)
"""

BINAH_SIGMA_PROMPT = """
Context: {context}
Decision Question: {decision_question}
Stakeholders: {stakeholders}
Constraints: {constraints}
Time Horizon: {time_horizon}

Apply the Binah-Σ methodology strictly:
1. Decompose the decision into its constituent elements
2. Analyze ethical implications and stakeholder impacts
3. Identify systemic risks and structural tensions
4. Synthesize coherence across all dimensions
5. Generate structured evaluation

Return ONLY valid JSON. No additional text.
"""


async def run_binah_sigma(data: dict) -> dict:
    """
    Execute Binah-Σ analysis with strict validation.

    Args:
        data: Dictionary with context, decision_question, stakeholders, constraints, time_horizon

    Returns:
        Validated BinahSigmaResponse as dictionary

    Raises:
        ValidationError: If LLM output doesn't match schema
        Exception: For other failures
    """
    prompt = BINAH_SIGMA_PROMPT.format(**data)

    try:
        # Mistral AI async call - run in executor since SDK is sync
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": BINAH_SIGMA_SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
        )

        raw_content = response.choices[0].message.content
        parsed = json.loads(raw_content)

        # 🔐 VALIDACIÓN CRÍTICA
        validated = BinahSigmaResponse(**parsed)

        logger.info(
            "BINAH-Σ OK | index=%.2f | confidence=%.2f",
            validated.binah_sigma_index,
            validated.binah_sigma_confidence
        )

        return validated.dict()

    except ValidationError as ve:
        logger.error(
            "BINAH-Σ SCHEMA VIOLATION",
            extra={"errors": ve.errors(), "raw": parsed if 'parsed' in locals() else None}
        )
        raise

    except Exception as e:
        logger.exception("BINAH-Σ ENGINE FAILURE")
        raise
