from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self) -> None:
        self._api_key: str = os.environ.get("GEMINI_API_KEY", "")
        self._model_name: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        self._available: bool = bool(self._api_key)

    async def generate_explanation(
        self,
        recommended_crop: str,
        estimated_profit: float,
        disease: str,
        pest_score: float,
        weather_score: float,
        market_score: float,
        overall_score: float,
        recommendation: str,
        warnings: list[str],
    ) -> str:
        if not self._available:
            return self._get_fallback_explanation(
                recommended_crop, estimated_profit, disease, overall_score, recommendation
            )

        try:
            import google.generativeai as genai

            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel(self._model_name)

            prompt = self._build_prompt(
                recommended_crop,
                estimated_profit,
                disease,
                pest_score,
                weather_score,
                market_score,
                overall_score,
                recommendation,
                warnings,
            )

            response = await model.generate_content_async(prompt)
            explanation = response.text.strip()
            logger.info("Gemini explanation generated successfully")
            return explanation
        except Exception as exc:
            logger.error("Gemini API failed: %s", exc)
            return self._get_fallback_explanation(
                recommended_crop, estimated_profit, disease, overall_score, recommendation
            )

    def _build_prompt(
        self,
        recommended_crop: str,
        estimated_profit: float,
        disease: str,
        pest_score: float,
        weather_score: float,
        market_score: float,
        overall_score: float,
        recommendation: str,
        warnings: list[str],
    ) -> str:
        warnings_text = "\n".join(f"- {w}" for w in warnings) if warnings else "None"
        return (
            f"You are an agricultural advisor.\n"
            f"Using the following structured outputs, generate a farmer-friendly explanation.\n"
            f"Do not change numerical predictions.\n\n"
            f"Recommended Crop: {recommended_crop}\n"
            f"Estimated Profit: Rs {estimated_profit}\n"
            f"Disease: {disease}\n"
            f"Pest Score: {pest_score}\n"
            f"Weather Score: {weather_score}\n"
            f"Market Score: {market_score}\n"
            f"Overall Score: {overall_score}\n"
            f"Recommendation: {recommendation}\n"
            f"Warnings: {warnings_text}\n\n"
            f"Provide a clear, concise explanation in simple language that a farmer can understand."
        )

    def _get_fallback_explanation(
        self,
        recommended_crop: str,
        estimated_profit: float,
        disease: str,
        overall_score: float,
        recommendation: str,
    ) -> str:
        return (
            f"{recommended_crop} is {recommendation.lower()} for your conditions. "
            f"Estimated profit is Rs {estimated_profit}. "
            f"Pest status: {disease}. "
            f"Overall score: {overall_score}. "
            f"Consult local agricultural experts for detailed guidance."
        )