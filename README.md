# Binah-Σ — Cognitive Decision Infrastructure

## Overview

**Binah-Σ** is a cognitive decision evaluation engine designed to analyze complex decisions through structured, ethical, and systemic lenses. Unlike generative chat systems, Binah-Σ produces **auditable, structured outputs** suitable for enterprise, policy, ESG, and compliance use cases.

### Key Differentiation

| Aspect | Traditional AI | Binah-Σ |
|--------|---------------|---------|
| Output | Text generation | Structured evaluation |
| Auditability | None | Native |
| Metrics | None | Numerical indices (0-1) |
| Use Case | Conversational | Critical decision-making |

---

## Features

- **Structured Decision Evaluation** — Not text generation, but measurable analysis
- **Strict JSON Schema Enforcement** — Every output validated by Pydantic
- **Async, Non-blocking API** — Built with FastAPI for high concurrency
- **Audit-Ready Logging** — Structured logging for compliance
- **LLM Vendor-Agnostic** — Easily swap underlying models
- **Production-Ready** — Error handling, health checks, CORS support

---

## Tech Stack

- **Python 3.10+**
- **FastAPI** (async web framework)
- **Pydantic** (schema validation)
- **OpenAI SDK** (pluggable LLM provider)
- **Uvicorn** (ASGI server)

---

## Project Structure

```
BinahSigma/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── engine.py            # Binah-Σ reasoning engine
│   ├── schemas.py           # Pydantic models
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
│
├── frontend/
│   └── index.html           # Demo UI
│
├── contexto.txt             # Project documentation
└── README.md                # This file
```

---

## Quick Start

### 1. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### Run the API

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

### 2. Frontend Setup

Simply open the HTML file in your browser:

```bash
cd frontend
# On Windows
start index.html

# On macOS
open index.html

# On Linux
xdg-open index.html
```

Or use a local server:

```bash
# Python
python -m http.server 8080

# Node.js
npx http-server -p 8080
```

Then navigate to: http://localhost:8080

---

## API Usage

### Endpoint

```
POST /binah-sigma/analyze
```

### Request Schema

```json
{
  "context": "string",
  "decision_question": "string",
  "stakeholders": ["string"],
  "constraints": ["string"],
  "time_horizon": "string"
}
```

### Response Schema

```json
{
  "binah_sigma_index": 0.0-1.0,
  "binah_sigma_confidence": 0.0-1.0,
  "decision_coherence": "Low|Medium|High",
  "ethical_alignment": "Aligned|Partial|Misaligned",
  "systemic_risk": "Low|Medium|High|Critical",
  "key_tensions": ["string"],
  "unintended_consequences": ["string"],
  "binah_recommendation": "string",
  "explanation_summary": "string",
  "analysis_version": "string"
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/binah-sigma/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Tech company considering mass layoffs to cut costs",
    "decision_question": "Should we lay off 30% of the workforce?",
    "stakeholders": ["employees", "investors", "customers", "community"],
    "constraints": ["budget deficit", "market pressure", "talent retention"],
    "time_horizon": "6 months"
  }'
```

---

## Deployment

### Docker (Recommended)

Create `Dockerfile` in `backend/`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t binah-sigma .
docker run -p 8000:8000 --env-file .env binah-sigma
```

### Cloud Platforms

#### Railway
```bash
railway login
railway init
railway up
```

#### Render
- Connect GitHub repo
- Set build command: `pip install -r requirements.txt`
- Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### AWS Lambda (with Mangum)
```bash
pip install mangum
# Add to main.py:
# from mangum import Mangum
# handler = Mangum(app)
```

---

## Use Cases

### Primary Markets

1. **Corporate Governance** — M&A, strategic decisions, risk assessment
2. **ESG & Compliance** — Policy evaluation, regulatory alignment
3. **Public Sector** — Policy analysis, public programs
4. **Financial Institutions** — High-impact investment decisions
5. **Multilateral Organizations** — Complex stakeholder decisions

### Example Scenarios

- Evaluating supply chain restructuring
- Assessing new product launch risks
- Analyzing regulatory compliance strategies
- Investment portfolio ethical alignment
- Public policy impact assessment

---

## Architecture

```
┌─────────────┐
│   Client    │
│ (Frontend)  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  FastAPI Gateway │
│  - CORS          │
│  - Validation    │
│  - Error Handling│
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Binah-Σ Engine   │
│  - Prompt Orch.  │
│  - LLM Call      │
│  - JSON Enforce  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Validation Layer │
│  - Pydantic      │
│  - Schema Check  │
└──────┬───────────┘
       │
       ├─────────────┐
       ▼             ▼
┌───────────┐  ┌──────────┐
│  Logging  │  │ Metrics  │
└───────────┘  └──────────┘
```

---

## Competitive Advantages

### Technical Advantages

1. **Schema-First Architecture** — LLM outputs are contracts, not suggestions
2. **Vendor Agnostic** — Swap OpenAI for Anthropic, local models, etc.
3. **Audit Trail** — Every decision is logged with structured metadata
4. **Metrics Accumulation** — Build longitudinal decision quality datasets

### Business Advantages

1. **Not a Chatbot** — Positioned for critical infrastructure
2. **Compliance-Ready** — Structured outputs for regulatory review
3. **Scalable Pricing** — Metered API usage, not seat-based
4. **Data Moat** — Aggregated decision quality benchmarks

---

## Roadmap

### Phase 1: MVP (Current)
- [x] Core API implementation
- [x] Schema validation
- [x] Basic frontend demo
- [x] Documentation

### Phase 2: Production Hardening
- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] Database persistence (PostgreSQL)
- [ ] Metrics dashboard
- [ ] Multi-model support (Anthropic, local LLMs)

### Phase 3: Enterprise Features
- [ ] Multi-tenancy
- [ ] Audit log export
- [ ] Custom prompt templates
- [ ] Batch analysis API
- [ ] White-label deployment

### Phase 4: Intelligence Layer
- [ ] Decision quality benchmarks
- [ ] Temporal analysis (track decisions over time)
- [ ] Comparative analysis (A/B decision evaluation)
- [ ] Risk alerts & notifications

---

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

---

## Security Considerations

### API Security

- Enable authentication before production deployment
- Implement rate limiting (e.g., using `slowapi`)
- Restrict CORS to specific domains
- Use environment variables for all secrets
- Enable HTTPS in production

### Data Privacy

- Do not log sensitive decision context
- Implement data retention policies
- Consider on-premise deployment for sensitive sectors
- Review OpenAI data usage policies

---

## Troubleshooting

### Common Issues

**Error: Module not found**
```bash
pip install -r requirements.txt
```

**Error: OpenAI API key not found**
- Ensure `.env` file exists in `backend/`
- Check that `OPENAI_API_KEY` is set correctly
- Restart the server after changing `.env`

**CORS errors in browser**
- Verify API is running on `localhost:8000`
- Check CORS middleware configuration in `main.py`

**JSON validation errors**
- Check LLM is returning valid JSON
- Review `engine.py` prompt instructions
- Inspect logs for validation error details

---

## License

**Proprietary / Confidential** — All rights reserved.

For licensing inquiries, contact the project maintainer.

---

## Contact & Support

For questions, issues, or partnership opportunities:

- **GitHub Issues**: [Report bugs and feature requests]
- **Email**: [Your contact email]
- **Documentation**: See `contexto.txt` for detailed architecture

---

**Binah-Σ**

*Cognitive infrastructure for measurable decisions.*
*Not chat. Not opinion. Structured judgment.*
