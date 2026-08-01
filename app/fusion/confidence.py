from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ConfidenceFusion:
    def __init__(self) -> None:
        self._default_weights: dict[str, float] = {
            "profit": 0.40,
            "pest": 0.25,
            "weather": 0.20,
            "market": 0.15,
        }

    def _adaptive_weights(
        self,
        pest_score: float,
        weather_score: float,
    ) -> dict[str, float]:
        weights = dict(self._default_weights)
        if pest_score < 40:
            weights["pest"] = 0.50
            weights["profit"] = 0.30
            weights["weather"] = 0.10
            weights["market"] = 0.10
        if weather_score < 40:
            weights["weather"] = 0.40
            weights["profit"] = 0.30
            weights["pest"] = 0.15
            weights["market"] = 0.15
        logger.info("Adaptive weights: %s", weights)
        return weights

    def compute_weighted_score(
        self,
        profit_score: float,
        pest_score: float,
        weather_score: float,
        market_score: float,
    ) -> float:
        weights = self._adaptive_weights(pest_score, weather_score)
        overall = (
            profit_score * weights["profit"]
            + pest_score * weights["pest"]
            + weather_score * weights["weather"]
            + market_score * weights["market"]
        )
        result = round(overall, 2)
        logger.info("Weighted overall score: %.2f", result)
        return result

    def compute_overall_confidence(
        self,
        profit_confidence: float,
        pest_confidence: float,
        weather_confidence: float,
        market_confidence: float,
    ) -> float:
        confidences = [
            profit_confidence,
            pest_confidence,
            weather_confidence,
            market_confidence,
        ]
        avg = sum(confidences) / len(confidences)
        result = round(avg * 100, 2)
        logger.info("Overall confidence: %.2f%%", result)
        return result

    def get_recommendation(self, overall_score: float) -> str:
        if overall_score >= 80:
            return "Highly Recommended"
        if overall_score >= 60:
            return "Recommended"
        if overall_score >= 40:
            return "Proceed Carefully"
        return "Not Recommended"