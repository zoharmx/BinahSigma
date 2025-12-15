from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from schemas import BinahSigmaRequest, BinahSigmaResponse
from engine import run_binah_sigma

app = FastAPI(
    title="Binah-Σ Decision Engine",
    description="Cognitive infrastructure for structured decision evaluation",
    version="1.0.0"
)

# Configurar CORS para permitir llamadas desde frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://binahsigma.onrender.com",  # Production frontend
        "http://localhost:3000",            # Local development
        "http://localhost:8000",            # Local development
        "http://127.0.0.1:3000",            # Local development
        "http://127.0.0.1:8000",            # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Binah-Σ Decision Engine",
        "status": "operational",
        "version": "1.0.0",
        "endpoint": "/binah-sigma/analyze"
    }


@app.post(
    "/binah-sigma/analyze",
    response_model=BinahSigmaResponse,
    summary="Run structured Binah-Σ decision analysis",
    description="Analyzes complex decisions through ethical, systemic, and structural lenses. Returns auditable, structured evaluation."
)
async def analyze_decision(payload: BinahSigmaRequest):
    """
    Execute Binah-Σ analysis on a decision.

    Args:
        payload: BinahSigmaRequest with context, question, stakeholders, constraints, time_horizon

    Returns:
        BinahSigmaResponse with structured evaluation metrics

    Raises:
        HTTPException 502: If LLM produces invalid output
        HTTPException 500: For internal engine errors
    """
    try:
        result = await run_binah_sigma(payload.dict())
        return result
    except ValidationError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Upstream reasoning engine produced invalid structured output",
                "validation_errors": e.errors()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal reasoning engine error",
                "message": str(e)
            }
        )


@app.get("/health")
async def health_check():
    """Kubernetes/Docker health check endpoint"""
    return {"status": "healthy"}
