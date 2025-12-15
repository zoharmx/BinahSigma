# 🚀 Quick Start - Binah-Σ v2.0

## ⚡ Start in 2 Minutes

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start v2 Server

```bash
python -m uvicorn main_v2:app --reload --host 0.0.0.0 --port 8000
```

### 3. Copy Demo API Keys

When the server starts, you'll see:

```
============================================================
DEMO API KEYS GENERATED
============================================================
Demo Tier:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Startup Tier: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
============================================================
```

**Copy both keys** and save them!

### 4. Open Enhanced Frontend

Open in browser: `frontend/index_v2.html`

Or use Python HTTP server:
```bash
cd frontend
python -m http.server 8080
```

Then open: http://localhost:8080/index_v2.html

---

## 🎮 Try These First

### Option A: Use the Frontend (Easiest)

1. Open `frontend/index_v2.html`
2. Click **"Elon Musk: Fire 50% of Twitter?"**
3. Scroll down and click **"Run Binah-Σ Analysis"**
4. See results with transparent scoring!

### Option B: Use the API

```bash
# Without auth (v1 - backward compatible)
curl -X POST http://localhost:8000/binah-sigma/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Startup with $5M ARR, 40% growth, VCs offering $20M at $100M valuation",
    "decision_question": "Should we raise Series A or stay bootstrapped?",
    "stakeholders": ["founders", "employees", "potential investors"],
    "constraints": ["control vs speed", "competition", "hiring needs"],
    "time_horizon": "3 years"
  }'
```

**Or with authentication (v2)**:

```bash
# Replace with your Startup tier key from console
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8000/v2/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "context": "Fortune 500 with 50K employees, real estate leases $200M/year",
    "decision_question": "Should we mandate 5 days/week return to office?",
    "stakeholders": ["employees", "management", "shareholders"],
    "constraints": ["lease commitments", "talent retention", "culture"],
    "time_horizon": "1 year",
    "provider": "mistral",
    "industry": "technology"
  }'
```

---

## 🎯 What to Test

### 1. Multi-Provider Support

Try different providers:

```bash
# Mistral (default)
{ ... "provider": "mistral" ... }

# Google Gemini
{ ... "provider": "gemini" ... }

# DeepSeek
{ ... "provider": "deepseek" ... }
```

Compare quality and speed!

### 2. Industry-Specific Scoring

Try different industries:

```bash
# Healthcare (40% weight on ethics)
{ ... "industry": "healthcare" ... }

# Finance (35% weight on feasibility)
{ ... "industry": "finance" ... }

# Nonprofit (40% weight on stakeholder benefit)
{ ... "industry": "nonprofit" ... }
```

Check `_metadata.scoring_breakdown` in response to see how weights change the index.

### 3. Rate Limiting

```bash
# Use Demo tier key (10 requests/month limit)
# Run 11 requests and see rate limit error on #11
```

### 4. Quality Validation

Try a vague request:

```bash
curl -X POST http://localhost:8000/v2/analyze \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "context": "A company",
    "decision_question": "Should we do something?",
    "stakeholders": ["people"],
    "constraints": ["things"],
    "time_horizon": "later"
  }'
```

Quality validator may reject it!

---

## 📊 Check Your Usage

```bash
curl http://localhost:8000/v2/usage \
  -H "Authorization: Bearer $API_KEY"
```

Response:
```json
{
  "current_usage": {
    "minute": 2,
    "day": 5,
    "month": 12
  },
  "limits": {
    "minute": 5,
    "day": 10,
    "month": 100
  },
  "tier": "startup",
  "customer_id": "startup_user"
}
```

---

## 📊 Check Provider Stats

```bash
curl http://localhost:8000/v2/stats \
  -H "Authorization: Bearer $API_KEY"
```

Response:
```json
{
  "mistral": {
    "provider": "MistralProvider",
    "model": "mistral-large-latest",
    "calls": 15,
    "total_tokens": 0
  },
  "gemini": {
    "provider": "GeminiProvider",
    "model": "gemini-1.5-flash",
    "calls": 3,
    "total_tokens": 0
  },
  "deepseek": {
    "provider": "DeepSeekProvider",
    "model": "deepseek-chat",
    "calls": 0,
    "total_tokens": 0
  }
}
```

---

## 🎨 Frontend Features

### Pre-loaded Examples

1. **Elon Musk: Fire 50% of Twitter?**
2. **Pharma: Donate Vaccines?**
3. **Startup: VC or Bootstrap?**
4. **OpenAI: Open-Source AGI?**
5. **Company: Net-Zero by 2030?**
6. **Return to Office Mandate?**

### Tabs

- **Pre-loaded Examples** - Click and analyze
- **Custom Analysis** - Build your own
- **Pricing** - See SaaS tiers

### Advanced Options

- **Provider Selection**: Choose Mistral, Gemini, or DeepSeek
- **Industry**: General, Healthcare, Finance, Tech, Nonprofit
- **API Key**: Use authenticated v2 endpoint

---

## 🔍 Understanding the Response

```json
{
  "binah_sigma_index": 0.68,
  "binah_sigma_confidence": 0.85,
  "decision_coherence": "Medium",
  "dimensions": {
    "clarity_score": 90,
    "stakeholder_benefit_score": 40,
    "feasibility_score": 85,
    "ethical_risk_level": "High"
  },
  "ethical_alignment": "Partial",
  "systemic_risk": "High",
  "key_tensions": [
    "Short-term revenue vs long-term customer trust",
    "Investor pressure vs customer flexibility",
    "Cash flow stability vs churn risk",
    "Sales incentives vs retention goals"
  ],
  "unintended_consequences": [
    "Increased CAC due to resistance",
    "Potential reputational damage",
    "Reduced product-market fit feedback",
    "Sales team burnout",
    "Higher churn post-annual term"
  ],
  "binah_recommendation": "Implement hybrid model with incentives...",
  "explanation_summary": "The forced annual subscription introduces high systemic risk...",
  "_metadata": {
    "provider_used": "mistral",
    "industry": "technology",
    "quality_score": 95.0,
    "scoring_breakdown": {
      "components": {
        "clarity": { "score": 90, "contribution": 0.18 },
        "stakeholder_benefit": { "score": 40, "contribution": 0.12 },
        "feasibility": { "score": 85, "contribution": 0.255 },
        "ethics": { "contribution": 0.06 }
      },
      "ethical_cap_applied": true,
      "final_index": 0.68
    },
    "usage": {
      "requests_remaining": {
        "minute": 4,
        "day": 95,
        "month": 87
      },
      "tier": "startup"
    }
  }
}
```

---

## 🎯 Key Metrics Explained

**binah_sigma_index** (0-1): Overall decision quality
- ≥0.75 = High coherence, low risk
- 0.5-0.75 = Medium complexity
- <0.5 = High risk, major tensions

**dimensions**: Raw scores from LLM
- clarity_score: How well-defined is the problem?
- stakeholder_benefit_score: Net benefit to all parties
- feasibility_score: Implementation likelihood
- ethical_risk_level: Ethical concerns (None/Low/Medium/High/Critical)

**scoring_breakdown**: Shows exactly how index was calculated
- Each dimension's contribution
- Whether ethical veto was applied

**quality_score**: Content quality (0-100)
- Based on depth, specificity, uniqueness

---

## 🐛 Troubleshooting

### "Module not found" errors

```bash
cd backend
pip install -r requirements.txt
```

### "Invalid API key"

The demo keys expire after 365 days. If needed, restart server to regenerate.

### "Rate limit exceeded"

Wait for the reset time shown in error, or use a higher tier key.

### CORS errors

Make sure server is running on port 8000 and frontend uses correct URL.

### Quality validation failures

Make the decision context more specific and detailed. Avoid vague language.

---

## 📚 Next Steps

1. **Read**: V2_IMPLEMENTATION_SUMMARY.md (comprehensive overview)
2. **Read**: MEJORAS_ANALYSIS.md (understand the improvements)
3. **Read**: IMPLEMENTATION_PLAN.md (6-week roadmap)
4. **Try**: All 6 pre-loaded examples
5. **Test**: Different providers and industries
6. **Build**: Your own integration

---

## 🎉 You're Ready!

Binah-Σ v2.0 is running with:
- ✅ 3 LLM providers
- ✅ Transparent scoring
- ✅ Quality validation
- ✅ Authentication
- ✅ Rate limiting
- ✅ Enhanced UI

**Now go analyze some decisions! 🚀**
