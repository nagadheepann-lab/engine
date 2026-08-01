from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ScoreCalculator:
    PROFIT_RANGES = [
        (10000, 20),
        (50000, 60),
        (100000, 100),
    ]

    PEST_SCORE_MAP = {
        "Healthy": 95,
        "Leaf Spot": 65,
        "Rust": 30,
    }

    WEATHER_SCORE_MAP = {
        "Excellent": 95,
        "Good": 80,
        "Poor": 20,
    }

    MARKET_SCORE_MAP = {
        "Rising": 90,
        "Stable": 70,
        "Falling": 30,
    }

    def calculate_pest_score(self, disease: str, confidence: float) -> float:
        base_score = self.PEST_SCORE_MAP.get(disease, 50)
        adjusted = base_score * confidence
        logger.debug("Pest score: disease=%s, confidence=%.2f, score=%.2f", disease, confidence, adjusted)
        return round(adjusted, 2)

    def calculate_weather_score(self, weather_data: dict[str, Any]) -> float:
        raw_score = weather_data.get("weather_score", 50)
        logger.debug("Weather score from service: %.2f", raw_score)
        return round(float(raw_score), 2)

    def calculate_market_score(self, market_data: dict[str, Any]) -> float:
        trend = market_data.get("trend", "Stable")
        raw_score = self.MARKET_SCORE_MAP.get(trend, 70)
        logger.debug("Market score: trend=%s, score=%.2f", trend, raw_score)
        return round(float(raw_score), 2)

    def calculate_profit_score(self, estimated_profit: float) -> float:
        if estimated_profit <= self.PROFIT_RANGES[0][0]:
            score = self.PROFIT_RANGES[0][1]
        elif estimated_profit <= self.PROFIT_RANGES[1][0]:
            ratio = (estimated_profit - self.PROFIT_RANGES[0][0]) / (
                self.PROFIT_RANGES[1][0] - self.PROFIT_RANGES[0][0]
            )
            score = self.PROFIT_RANGES[0][1] + ratio * (
                self.PROFIT_RANGES[1][1] - self.PROFIT_RANGES[0][1]
            )
        elif estimated_profit <= self.PROFIT_RANGES[2][0]:
            ratio = (estimated_profit - self.PROFIT_RANGES[1][0]) / (
                self.PROFIT_RANGES[2][0] - self.PROFIT_RANGES[1][0]
            )
            score = self.PROFIT_RANGES[1][1] + ratio * (
                self.PROFIT_RANGES[2][1] - self.PROFIT_RANGES[1][1]
            )
        else:
            score = self.PROFIT_RANGES[2][1]

        logger.debug("Profit score: profit=%.2f, score=%.2f", estimated_profit, score)
        return round(score, 2)

    def get_all_scores(
        self,
        estimated_profit: float,
        pest_score: float,
        weather_score: float,
        market_score: float,
    ) -> dict[str, float]:
        return {
            "profit_score": self.calculate_profit_score(estimated_profit),
            "pest_score": pest_score,
            "weather_score": weather_score,
            "market_score": market_score,
        }