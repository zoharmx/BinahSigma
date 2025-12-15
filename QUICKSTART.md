# Binah-Σ — Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure API Key

```bash
# Copy template
cp .env.example .env

# Edit .env and add your OpenAI key
# OPENAI_API_KEY=sk-your-key-here
```

On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
notepad .env
```

### Step 3: Start Backend

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 4: Test API

Open browser to: **http://localhost:8000/docs**

You'll see the interactive Swagger UI.

### Step 5: Open Frontend

```bash
cd ../frontend
```

Then open `index.html` in your browser, or run:

```bash
# Python
python -m http.server 8080

# Then open http://localhost:8080
```

---

## ✅ Verify Installation

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test Analysis Endpoint

```bash
curl -X POST http://localhost:8000/binah-sigma/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Small startup considering venture capital funding",
    "decision_question": "Should we accept Series A funding?",
    "stakeholders": ["founders", "employees", "potential investors"],
    "constraints": ["dilution concerns", "growth pressure", "autonomy"],
    "time_horizon": "2 years"
  }'
```

---

## 🎯 Example Use Cases to Try

### Corporate Decision
```json
{
  "context": "Fortune 500 company evaluating remote work policy",
  "decision_question": "Should we mandate return to office 5 days/week?",
  "stakeholders": ["employees", "management", "real estate", "productivity"],
  "constraints": ["lease commitments", "talent retention", "culture"],
  "time_horizon": "1 year"
}
```

### ESG Policy
```json
{
  "context": "Manufacturing company considering carbon neutrality commitment",
  "decision_question": "Should we commit to net-zero by 2030?",
  "stakeholders": ["shareholders", "customers", "regulators", "environment"],
  "constraints": ["technology costs", "supply chain", "competitive pressure"],
  "time_horizon": "7 years"
}
```

### Product Strategy
```json
{
  "context": "SaaS platform considering freemium model",
  "decision_question": "Should we offer a free tier to accelerate growth?",
  "stakeholders": ["users", "investors", "sales team", "support"],
  "constraints": ["server costs", "conversion rate", "brand positioning"],
  "time_horizon": "18 months"
}
```

---

## 🔧 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY not found"
- Check `.env` file exists in `backend/` folder
- Verify key starts with `sk-`
- Restart server after editing `.env`

### CORS errors in frontend
- Ensure backend is running on port 8000
- Clear browser cache
- Try opening frontend via http-server instead of file://

### JSON validation errors
- Check OpenAI API is responding
- Verify you have API credits
- Review logs in terminal for detailed errors

---

## 📊 Understanding the Output

### Key Metrics

- **binah_sigma_index** (0-1): Overall decision quality score
- **binah_sigma_confidence** (0-1): Model's confidence in analysis
- **decision_coherence**: Internal consistency (Low/Medium/High)
- **ethical_alignment**: Stakeholder value alignment
- **systemic_risk**: Unintended consequence risk level

### Interpreting Results

**Index > 0.7** → Strong coherence, low tension
**Index 0.4-0.7** → Moderate complexity, review tensions
**Index < 0.4** → High risk, significant structural issues

**Always review**:
- `key_tensions` — Main trade-offs
- `unintended_consequences` — Second-order effects
- `binah_recommendation` — Synthesized guidance

---

## 🎓 Next Steps

1. **Try your own decisions** — Use real organizational scenarios
2. **Compare decisions** — Run variations to see impact
3. **Build integrations** — Connect to your tools via API
4. **Customize prompts** — Edit `engine.py` for domain-specific analysis

---

## 🚢 Deploy to Production

### Quick Deploy Options

**Railway** (easiest):
```bash
railway login
railway init
railway up
```

**Render** (free tier):
1. Push to GitHub
2. Connect repo to Render
3. Deploy as Web Service

**Docker** (flexible):
```bash
docker build -t binah-sigma backend/
docker run -p 8000:8000 --env-file backend/.env binah-sigma
```

See full README.md for detailed deployment instructions.

---

## 💡 Tips

- Start with simple decisions to understand output format
- Use specific, measurable constraints
- Frame questions clearly and precisely
- Review all output fields, not just the index
- Track decisions over time for pattern analysis

---

**You're ready to run Binah-Σ!**

Questions? Check README.md or review contexto.txt for architecture details.
