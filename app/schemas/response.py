from __future__ import annotations

from pydantic import BaseModel, Field


class DecisionResponse(BaseModel):
    recommended_crop: str = Field(..., description="The recommended oilseed crop")
    estimated_profit: float = Field(..., description="Estimated profit in INR")
    disease: str = Field(..., description="Pest/disease prediction result")
    pest_score: float = Field(..., ge=0, le=100, description="Pest health normalized score")
    weather_score: float = Field(..., ge=0, le=100, description="Weather condition normalized score")
    market_score: float = Field(..., ge=0, le=100, description="Market condition normalized score")
    overall_score: float = Field(..., ge=0, le=100, description="Weighted overall score")
    confidence: float = Field(..., ge=0, le=100, description="Overall confidence percentage")
    recommendation: str = Field(..., description="Final recommendation label")
    warnings: list[str] = Field(default_factory=list, description="Rule engine warnings")
    explanation: str = Field(..., description="Gemini-generated farmer-friendly explanation")

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommended_crop": "Groundnut",
                "estimated_profit": 82400,
                "disease": "Healthy",
                "pest_score": 94,
                "weather_score": 86,
                "market_score": 78,
                "overall_score": 88,
                "confidence": 91,
                "recommendation": "Highly Recommended",
                "warnings": [],
                "explanation": "Groundnut is recommended because...",
            }
        }
    }