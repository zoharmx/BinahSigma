"""
Binah-Σ API v2.0 - Enterprise-Ready Decision Engine

Features:
- Multi-provider LLM support (Mistral, Gemini, DeepSeek)
- Transparent scoring algorithm
- Quality validation
- API key authentication
- Tier-based rate limiting
- Usage tracking
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from typing import Dict

from schemas import BinahSigmaRequest, BinahSigmaResponse
from engine_v2 import run_binah_sigma, get_provider_stats, switch_provider
from auth import APIKeyAuth, Tier
from rate_limiter import rate_limiter, usage_tracker

app = FastAPI(
    title="Binah-Σ Decision Engine v2.0",
    description="Enterprise cognitive infrastructure for structured decision evaluation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://binahsigma.onrender.com",  # Production frontend
        "binah-sigma.vercel.app",           # Production frontend
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
    """API information and health check"""
    return {
        "service": "Binah-Σ Decision Engine",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Multi-provider LLM support (Mistral, Gemini, DeepSeek)",
            "Transparent scoring algorithm",
            "Quality validation",
            "Tier-based rate limiting",
            "API key authentication"
        ],
        "endpoints": {
            "analyze": "/v2/analyze",
            "stats": "/v2/stats",
            "usage": "/v2/usage",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Kubernetes/Docker health check"""
    return {"status": "healthy", "version": "2.0.0"}


@app.post(
    "/v2/analyze",
    response_model=BinahSigmaResponse,
    summary="Run Binah-Σ decision analysis (v2)",
    description="Analyzes complex decisions with transparent scoring, quality validation, and multi-provider support"
)
async def analyze_decision_v2(
    payload: BinahSigmaRequest,
    auth_data: dict = Depends(APIKeyAuth.verify_api_key)
):
    """
    Execute Binah-Σ analysis with v2 enhancements.

    Requires:
        - Valid API key in Authorization header (Bearer token)

    Args:
        payload: Decision context and parameters
        auth_data: Authenticated user data (from dependency)

    Returns:
        BinahSigmaResponse: Structured evaluation with transparent scoring

    Raises:
        HTTPException 401: Invalid/expired API key
        HTTPException 429: Rate limit exceeded
        HTTPException 500: Internal error
        HTTPException 502: LLM quality validation failed
    """
    customer_id = auth_data["sub"]
    tier = auth_data.get("tier", Tier.DEMO)

    # Check rate limits
    try:
        usage_info = await rate_limiter.check_rate_limit(customer_id, tier)
    except HTTPException as e:
        # Rate limit exceeded
        raise e

    # Execute analysis
    try:
        result = await run_binah_sigma(
            data=payload.dict(exclude={"provider", "industry"}),
            provider=payload.provider,
            industry=payload.industry
        )

        # Record successful request
        usage_tracker.record_request(customer_id)

        # Add usage info to response metadata
        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"]["usage"] = {
            "requests_remaining": {
                "minute": usage_info["limits"]["minute"] - usage_info["minute"] - 1,
                "day": usage_info["limits"]["day"] - usage_info["day"] - 1,
                "month": usage_info["limits"]["month"] - usage_info["month"] - 1
            },
            "tier": tier
        }

        return result

    except ValidationError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Quality validation failed",
                "message": "LLM output did not meet quality standards",
                "validation_errors": e.errors()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Quality validation failed",
                "message": str(e)
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


@app.get(
    "/v2/stats",
    summary="Get LLM provider statistics",
    description="View usage statistics for all LLM providers"
)
async def get_stats(
    auth_data: dict = Depends(APIKeyAuth.verify_api_key)
):
    """Get LLM provider statistics (authenticated)"""
    return get_provider_stats()


@app.get(
    "/v2/usage",
    summary="Get your API usage",
    description="View your current API usage across all periods"
)
async def get_usage(
    auth_data: dict = Depends(APIKeyAuth.verify_api_key)
):
    """Get usage statistics for authenticated user"""
    customer_id = auth_data["sub"]
    tier = auth_data.get("tier", Tier.DEMO)

    stats = usage_tracker.get_customer_stats(customer_id)

    # Add limits
    stats["limits"] = {
        "minute": rate_limiter.tracker.tracker.get_limit(tier, "requests_per_minute"),
        "day": rate_limiter.tracker.tracker.get_limit(tier, "requests_per_day"),
        "month": rate_limiter.tracker.tracker.get_limit(tier, "requests_per_month")
    }

    stats["tier"] = tier
    stats["customer_id"] = customer_id

    return stats


@app.post(
    "/v2/admin/switch-provider",
    summary="Switch primary LLM provider (admin)",
    description="Change the primary LLM provider for all requests"
)
async def admin_switch_provider(
    provider: str,
    auth_data: dict = Depends(APIKeyAuth.verify_api_key)
):
    """Switch primary LLM provider (enterprise only)"""
    tier = auth_data.get("tier", Tier.DEMO)

    if tier != Tier.ENTERPRISE:
        raise HTTPException(
            status_code=403,
            detail="Provider switching is only available for Enterprise tier"
        )

    try:
        switch_provider(provider)
        return {
            "success": True,
            "provider": provider,
            "message": f"Switched primary provider to {provider}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Legacy v1 endpoint (backward compatibility)
@app.post(
    "/binah-sigma/analyze",
    response_model=BinahSigmaResponse,
    summary="Run Binah-Σ analysis (v1 - deprecated)",
    deprecated=True
)
async def analyze_decision_v1(payload: BinahSigmaRequest):
    """
    Legacy v1 endpoint (no authentication required for backward compatibility).

    WARNING: This endpoint is deprecated and will be removed in v3.
    Please migrate to /v2/analyze with API key authentication.
    """
    try:
        result = await run_binah_sigma(
            data=payload.dict(exclude={"provider", "industry"}),
            provider=payload.provider,
            industry=payload.industry
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Analysis failed", "message": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
