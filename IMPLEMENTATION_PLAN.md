# Plan de Implementación - Mejoras Prioritarias

**Basado en**: MEJORAS_ANALYSIS.md
**Timeline**: 6 semanas para Fase 2 completa
**Objetivo**: Sistema enterprise-ready con primeros clientes piloto

---

## 🎯 SEMANA 1: FOUNDATION (Crítico)

### Día 1-2: Validación de Calidad del Razonamiento

**Archivo**: `backend/quality_validator.py` (NUEVO)

```python
from typing import List
from schemas import BinahSigmaResponse


class QualityValidator:
    """Validates that LLM outputs meet minimum quality standards"""

    FORBIDDEN_GENERIC_PHRASES = [
        "it depends",
        "consider all options",
        "evaluate carefully",
        "there are pros and cons",
        "further analysis needed",
        "consult with experts"
    ]

    MIN_TENSIONS = 3
    MIN_CONSEQUENCES = 4
    MIN_RECOMMENDATION_LENGTH = 50

    @classmethod
    def validate(cls, response: BinahSigmaResponse) -> None:
        """
        Validates response quality. Raises ValueError if quality is insufficient.
        """
        errors = []

        # Check for generic recommendations
        rec_lower = response.binah_recommendation.lower()
        for phrase in cls.FORBIDDEN_GENERIC_PHRASES:
            if phrase in rec_lower:
                errors.append(f"Generic phrase detected: '{phrase}'")

        # Check minimum depth
        if len(response.key_tensions) < cls.MIN_TENSIONS:
            errors.append(
                f"Insufficient tensions: {len(response.key_tensions)} < {cls.MIN_TENSIONS}"
            )

        if len(response.unintended_consequences) < cls.MIN_CONSEQUENCES:
            errors.append(
                f"Insufficient consequences: {len(response.unintended_consequences)} < {cls.MIN_CONSEQUENCES}"
            )

        # Check recommendation quality
        if len(response.binah_recommendation) < cls.MIN_RECOMMENDATION_LENGTH:
            errors.append(
                f"Recommendation too short: {len(response.binah_recommendation)} chars"
            )

        # Check for empty/placeholder content
        if any(
            item.lower().strip() in ["n/a", "none", "tbd", ""]
            for item in response.key_tensions + response.unintended_consequences
        ):
            errors.append("Placeholder content detected in arrays")

        if errors:
            raise ValueError(
                f"Quality validation failed: {'; '.join(errors)}"
            )
```

**Integración en `engine.py`**:

```python
from quality_validator import QualityValidator

async def run_binah_sigma(data: dict) -> dict:
    # ... existing code ...

    validated = BinahSigmaResponse(**parsed)

    # NEW: Quality validation
    try:
        QualityValidator.validate(validated)
    except ValueError as e:
        logger.warning(f"Quality validation failed: {e}")
        # Option 1: Retry with stronger prompt
        # Option 2: Return error to user
        raise

    logger.info(...)
    return validated.dict()
```

**Testing**:
```bash
# Create test with intentionally bad output
python -m pytest tests/test_quality_validator.py
```

---

### Día 3-5: Authentication & Rate Limiting

**Dependencias nuevas** (`requirements.txt`):
```
slowapi>=0.1.9
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

**Archivo**: `backend/auth.py` (NUEVO)

```python
import os
from fastapi import Security, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from jose import JWTError, jwt

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"


class APIKeyAuth:
    """Simple API key authentication"""

    @staticmethod
    def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
        """Verify API key from Authorization header"""
        api_key = credentials.credentials

        # For MVP: Check against environment variable
        # For production: Check against database
        valid_keys = os.getenv("VALID_API_KEYS", "").split(",")

        if api_key not in valid_keys:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        return api_key


def create_api_key(customer_id: str, tier: str = "startup") -> str:
    """Generate a new API key (JWT token)"""
    payload = {
        "sub": customer_id,
        "tier": tier,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=365)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_api_key(token: str) -> dict:
    """Decode and validate API key"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
```

**Archivo**: `backend/rate_limiter.py` (NUEVO)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Tier-based limits
RATE_LIMITS = {
    "startup": "100/month",  # 100 requests per month
    "professional": "1000/month",
    "enterprise": "10000/month"
}
```

**Actualizar `main.py`**:

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from auth import APIKeyAuth
from rate_limiter import limiter

app = FastAPI(...)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/binah-sigma/analyze")
@limiter.limit("10/minute")  # Global rate limit
async def analyze_decision(
    request: Request,
    payload: BinahSigmaRequest,
    api_key: str = Depends(APIKeyAuth.verify_api_key)
):
    # TODO: Check tier-specific limits from api_key
    result = await run_binah_sigma(payload.dict())
    return result
```

**Setup inicial**:

```bash
# .env
JWT_SECRET_KEY=generate_strong_random_key_here
VALID_API_KEYS=test_key_123,demo_key_456

# Generate proper secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🎯 SEMANA 2: TRANSPARENCY ENGINE

### Día 6-10: Algoritmo de Scoring Transparente

**Archivo**: `backend/scoring_engine.py` (NUEVO)

```python
from typing import Literal
from pydantic import BaseModel, Field


class DecisionDimensions(BaseModel):
    """Granular dimensions evaluated by LLM"""
    clarity_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="How well-defined is the problem and context"
    )
    stakeholder_benefit_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Net benefit for all stakeholders"
    )
    feasibility_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Probability of successful implementation"
    )
    ethical_risk_level: Literal["None", "Low", "Medium", "High", "Critical"] = Field(
        ...,
        description="Detected ethical risk level"
    )


class ScoringEngine:
    """Deterministic index calculation from LLM dimensions"""

    def __init__(self, industry: str = "general"):
        """
        Args:
            industry: Can adjust weights per industry (future feature)
        """
        self.industry = industry

        # Configurable weights (sum to 1.0)
        self.weights = {
            "clarity": 0.20,
            "stakeholder": 0.30,
            "feasibility": 0.30,
            "ethics": 0.20
        }

        # Ethical risk penalties
        self.ethical_penalties = {
            "None": 1.0,
            "Low": 0.9,
            "Medium": 0.6,
            "High": 0.3,
            "Critical": 0.0
        }

        # Veto thresholds
        self.ethical_caps = {
            "Critical": 0.40,  # Never exceed 0.40
            "High": 0.60       # Never exceed 0.60
        }

    def calculate_index(self, dimensions: DecisionDimensions) -> float:
        """
        Calculate Binah-Σ Index from dimensions.

        Returns:
            float: Index between 0.0 and 1.0
        """
        # Normalize to 0-1
        s_clarity = dimensions.clarity_score / 100.0
        s_benefit = dimensions.stakeholder_benefit_score / 100.0
        s_feasibility = dimensions.feasibility_score / 100.0

        # Convert ethical risk to score
        risk_level = dimensions.ethical_risk_level
        s_ethics = self.ethical_penalties[risk_level]

        # Weighted average
        raw_index = (
            (s_clarity * self.weights["clarity"]) +
            (s_benefit * self.weights["stakeholder"]) +
            (s_feasibility * self.weights["feasibility"]) +
            (s_ethics * self.weights["ethics"])
        )

        # Apply ethical veto
        if risk_level in self.ethical_caps:
            raw_index = min(raw_index, self.ethical_caps[risk_level])

        return round(raw_index, 2)

    def derive_coherence(self, index: float) -> str:
        """Derive coherence level from index"""
        if index >= 0.75:
            return "High"
        elif index >= 0.5:
            return "Medium"
        else:
            return "Low"

    def derive_confidence(self, dimensions: DecisionDimensions) -> float:
        """
        Calculate confidence based on dimension variance.
        Lower variance = higher confidence
        """
        scores = [
            dimensions.clarity_score,
            dimensions.stakeholder_benefit_score,
            dimensions.feasibility_score
        ]

        # Simple heuristic: if all scores agree (all high or all low), confidence is high
        score_range = max(scores) - min(scores)
        confidence = 1.0 - (score_range / 100.0)

        return round(confidence, 2)
```

**Actualizar `schemas.py`**:

```python
from scoring_engine import DecisionDimensions

class BinahSigmaResponse(BaseModel):
    # Calculated by Python (not LLM)
    binah_sigma_index: float
    binah_sigma_confidence: float
    decision_coherence: str

    # NEW: Transparent breakdown
    dimensions: DecisionDimensions

    # Rest stays same
    ethical_alignment: str
    systemic_risk: str
    key_tensions: List[str]
    unintended_consequences: List[str]
    binah_recommendation: str
    explanation_summary: str
    analysis_version: str
```

**Actualizar prompt en `engine.py`**:

```python
BINAH_SIGMA_SYSTEM = """
You are Binah-Σ, a deep synthesis reasoning engine.

OUTPUT SCHEMA:
You must return JSON with these fields:

1. dimensions (object):
   - clarity_score (0-100): How clear is the problem definition?
   - stakeholder_benefit_score (0-100): Net benefit to all parties
   - feasibility_score (0-100): Likelihood of successful execution
   - ethical_risk_level ("None"|"Low"|"Medium"|"High"|"Critical"): Ethical concerns

2. ethical_alignment (string): "Aligned" | "Partial" | "Misaligned"
3. systemic_risk (string): "Low" | "Medium" | "High" | "Critical"
4. key_tensions (array): Minimum 4 structural tensions
5. unintended_consequences (array): Minimum 5 second-order effects
6. binah_recommendation (string): Concrete, actionable recommendation
7. explanation_summary (string): Brief rationale
8. analysis_version (string): "v1.0"

DO NOT generate binah_sigma_index, binah_sigma_confidence, or decision_coherence.
These will be calculated deterministically.
"""
```

**Integrar en `engine.py`**:

```python
from scoring_engine import ScoringEngine, DecisionDimensions

scorer = ScoringEngine()

async def run_binah_sigma(data: dict) -> dict:
    # ... LLM call ...

    # Parse LLM output
    parsed = json.loads(raw_content)

    # Extract dimensions
    dimensions = DecisionDimensions(**parsed["dimensions"])

    # Calculate index deterministically
    calculated_index = scorer.calculate_index(dimensions)
    calculated_confidence = scorer.derive_confidence(dimensions)
    calculated_coherence = scorer.derive_coherence(calculated_index)

    # Build final response
    final_response = {
        "binah_sigma_index": calculated_index,
        "binah_sigma_confidence": calculated_confidence,
        "decision_coherence": calculated_coherence,
        "dimensions": dimensions.dict(),
        **{k: v for k, v in parsed.items() if k != "dimensions"}
    }

    # Validate
    validated = BinahSigmaResponse(**final_response)
    QualityValidator.validate(validated)

    return validated.dict()
```

---

## 🎯 SEMANA 3-4: VALIDATION & CASE STUDIES

### Caso Histórico #1: Template

**Archivo**: `case_studies/blockbuster_netflix_2000.json`

```json
{
  "metadata": {
    "title": "Blockbuster vs Netflix Acquisition (2000)",
    "industry": "Entertainment / Retail",
    "date": "2000-09",
    "source": "Harvard Business Review, Forbes",
    "binah_analysis_date": "2025-12-14"
  },

  "decision_context": {
    "context": "Blockbuster is the dominant video rental chain with 9,000 stores and $5B revenue. Netflix, a 3-year-old DVD-by-mail startup with 300K subscribers, has approached Blockbuster about a $50M acquisition. Netflix is losing money and needs capital.",
    "decision_question": "Should Blockbuster acquire Netflix for $50 million?",
    "stakeholders": [
      "Blockbuster shareholders",
      "Blockbuster store franchisees",
      "Blockbuster employees",
      "Netflix founders",
      "Customers (rental market)"
    ],
    "constraints": [
      "Blockbuster's core revenue from late fees ($800M/year)",
      "Physical store infrastructure already built",
      "Netflix business model unproven",
      "Board skeptical of internet companies (post dot-com bubble)"
    ],
    "time_horizon": "5 years"
  },

  "actual_outcome": {
    "decision_made": "Blockbuster declined to acquire Netflix",
    "key_moments": [
      "2000: Blockbuster passes on $50M deal",
      "2004: Blockbuster launches 'Blockbuster Online' (too late)",
      "2010: Blockbuster files for bankruptcy",
      "2013: Last Blockbuster stores close",
      "2025: Netflix worth $150B+"
    ],
    "consequences": [
      "Blockbuster destroyed by inability to adapt to streaming",
      "Lost $5B in market value",
      "40,000+ employees lost jobs",
      "Netflix became dominant entertainment platform",
      "Late fee model became obsolete"
    ]
  },

  "binah_analysis": null,
  "comparison": null
}
```

**Script**: `tools/analyze_historical.py`

```python
import json
import asyncio
from pathlib import Path
from engine import run_binah_sigma

async def analyze_case_study(case_file: Path):
    """Analyze a historical case and compare to actual outcome"""

    with open(case_file) as f:
        case = json.load(f)

    # Run Binah-Σ analysis
    result = await run_binah_sigma(case["decision_context"])

    # Compare to actual outcome
    comparison = {
        "binah_recommended": result["binah_recommendation"],
        "actual_decision": case["actual_outcome"]["decision_made"],
        "match": "MATCH" if similar(
            result["binah_recommendation"],
            case["actual_outcome"]["decision_made"]
        ) else "MISMATCH",
        "consequences_predicted": len([
            c for c in result["unintended_consequences"]
            if any(ac in c for ac in case["actual_outcome"]["consequences"])
        ]),
        "total_consequences": len(case["actual_outcome"]["consequences"])
    }

    # Save results
    case["binah_analysis"] = result
    case["comparison"] = comparison

    output_file = case_file.parent / f"{case_file.stem}_analyzed.json"
    with open(output_file, "w") as f:
        json.dump(case, f, indent=2)

    print(f"✅ Analyzed: {case['metadata']['title']}")
    print(f"   Binah-Σ Index: {result['binah_sigma_index']}")
    print(f"   Match: {comparison['match']}")
    print(f"   Consequences predicted: {comparison['consequences_predicted']}/{comparison['total_consequences']}")

if __name__ == "__main__":
    asyncio.run(analyze_case_study(Path("case_studies/blockbuster_netflix_2000.json")))
```

**Objetivo Semana 3-4**:
- ✅ 3 casos históricos documentados
- ✅ Script de análisis automatizado
- ✅ Comparación quantitativa (% de consecuencias predichas)
- ✅ Material para white paper

---

## 🎯 SEMANA 5-6: BUSINESS READINESS

### Pricing Page & Customer Dashboard

**Archivo**: `frontend/pricing.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>Binah-Σ Pricing</title>
</head>
<body>
  <h1>Pricing Plans</h1>

  <div class="tier">
    <h2>Startup</h2>
    <p class="price">$99/month</p>
    <ul>
      <li>100 analyses/month</li>
      <li>JSON API access</li>
      <li>Email support</li>
      <li>14-day free trial</li>
    </ul>
    <button>Start Free Trial</button>
  </div>

  <div class="tier featured">
    <h2>Professional</h2>
    <p class="price">$499/month</p>
    <ul>
      <li>1,000 analyses/month</li>
      <li>Priority support</li>
      <li>Webhook integrations</li>
      <li>White-label PDF exports</li>
      <li>Team collaboration (5 users)</li>
    </ul>
    <button>Start Free Trial</button>
  </div>

  <div class="tier">
    <h2>Enterprise</h2>
    <p class="price">Custom</p>
    <ul>
      <li>Unlimited analyses</li>
      <li>On-premise deployment</li>
      <li>Custom model fine-tuning</li>
      <li>SLA 99.9%</li>
      <li>Dedicated success manager</li>
    </ul>
    <button>Contact Sales</button>
  </div>
</body>
</html>
```

### Usage Tracking

**Archivo**: `backend/usage_tracker.py`

```python
from datetime import datetime
from typing import Dict

class UsageTracker:
    """Track API usage per customer"""

    def __init__(self):
        # In production: use PostgreSQL
        self.usage = {}  # {api_key: {month: count}}

    def record_analysis(self, api_key: str):
        """Record one analysis"""
        month_key = datetime.now().strftime("%Y-%m")

        if api_key not in self.usage:
            self.usage[api_key] = {}

        if month_key not in self.usage[api_key]:
            self.usage[api_key][month_key] = 0

        self.usage[api_key][month_key] += 1

    def get_usage(self, api_key: str, month: str = None) -> int:
        """Get usage count for a customer"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        return self.usage.get(api_key, {}).get(month, 0)

    def check_limit(self, api_key: str, tier: str) -> bool:
        """Check if customer is within tier limits"""
        limits = {
            "startup": 100,
            "professional": 1000,
            "enterprise": float('inf')
        }

        usage = self.get_usage(api_key)
        return usage < limits.get(tier, 0)
```

---

## 📊 SUCCESS METRICS

### Semana 1
- ✅ Quality validator catches 90%+ generic outputs
- ✅ Auth system functional with test API keys
- ✅ Rate limiting prevents abuse

### Semana 2
- ✅ Scoring engine produces deterministic indices
- ✅ Ethical veto prevents dangerous recommendations from scoring high
- ✅ All existing tests pass with new schema

### Semana 3-4
- ✅ 3 case studies completed
- ✅ At least 60% of real consequences predicted
- ✅ Draft white paper written

### Semana 5-6
- ✅ Pricing page live
- ✅ Stripe integration ready
- ✅ Usage tracking accurate
- ✅ 5 beta users signed up

---

## 🚀 DEPLOYMENT CHECKLIST

```bash
# Pre-launch checklist
□ All tests passing
□ Quality validator enabled
□ Auth system tested
□ Rate limiting configured
□ Scoring engine validated
□ 3 case studies documented
□ Pricing page deployed
□ Stripe test mode working
□ Email notifications setup
□ Error monitoring (Sentry)
□ Usage dashboard functional

# Launch
□ Announce on LinkedIn
□ Send to 20 warm leads
□ Post on Product Hunt
□ Tweet thread with case study
□ Email existing waitlist
```

---

**TOTAL TIMELINE**: 6 semanas para sistema enterprise-ready
**EXPECTED OUTCOME**: Producto vendible con validación científica
