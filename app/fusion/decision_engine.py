from __future__ import annotations

import logging
from typing import Any

from app.ml.pest_service import PestService
from app.ml.profit_service import ProfitService
from app.rules.validator import RuleEngine
from app.schemas.request import DecisionRequest
from app.schemas.response import DecisionResponse
from app.services.gemini_service import GeminiService
from app.services.market_service import MarketService
from app.services.weather_service import WeatherService
from app.fusion.score_calculator import ScoreCalculator
from app.fusion.confidence import ConfidenceFusion

logger = logging.getLogger(__name__)


class DecisionEngine:
    def __init__(
        self,
        pest_service: PestService | None = None,
        profit_service: ProfitService | None = None,
        weather_service: WeatherService | None = None,
        market_service: MarketService | None = None,
        gemini_service: GeminiService | None = None,
        rule_engine: RuleEngine | None = None,
        score_calculator: ScoreCalculator | None = None,
        confidence_fusion: ConfidenceFusion | None = None,
    ) -> None:
        self._pest_service = pest_service or PestService()
        self._profit_service = profit_service or ProfitService()
        self._weather_service = weather_service or WeatherService()
        self._market_service = market_service or MarketService()
        self._gemini_service = gemini_service or GeminiService()
        self._rule_engine = rule_engine or RuleEngine()
        self._score_calculator = score_calculator or ScoreCalculator()
        self._confidence_fusion = confidence_fusion or ConfidenceFusion()

    async def run(self, request: DecisionRequest) -> DecisionResponse:
        logger.info("Starting decision engine for crop: %s", request.crop)

        pest_result = self._pest_service.predict(request.image_upload or "")
        logger.info("Pest service result: %s", pest_result)

        profit_result = self._profit_service.predict(
            temperature=request.temperature,
            humidity=request.humidity,
            rainfall=request.rainfall,
            budget=request.budget,
            land_area=request.land_area,
            expected_selling_price=request.expected_selling_price,
        )
        logger.info("Profit service result: %s", profit_result)

        weather_result = await self._weather_service.get_weather(
            request.state, request.district
        )
        logger.info("Weather service result: %s", weather_result)

        market_result = await self._market_service.get_market_data(request.crop)
        logger.info("Market service result: %s", market_result)

        rule_result = self._rule_engine.validate(
            crop=request.crop,
            budget=request.budget,
            water_availability=request.water_availability,
            temperature=request.temperature,
            land_area=request.land_area,
        )
        logger.info("Rule engine result: %s", rule_result)

        scores = self._score_calculator.get_all_scores(
            estimated_profit=profit_result["estimated_profit"],
            pest_score=pest_result["confidence"] * 100,
            weather_score=weather_result["weather_score"],
            market_score=market_result["market_score"],
        )
        logger.info("All scores: %s", scores)

        overall_score = self._confidence_fusion.compute_weighted_score(
            profit_score=scores["profit_score"],
            pest_score=scores["pest_score"],
            weather_score=scores["weather_score"],
            market_score=scores["market_score"],
        )

        overall_confidence = self._confidence_fusion.compute_overall_confidence(
            profit_confidence=profit_result["confidence"],
            pest_confidence=pest_result["confidence"],
            weather_confidence=weather_result["weather_score"] / 100,
            market_confidence=market_result["market_score"] / 100,
        )

        recommendation = self._confidence_fusion.get_recommendation(overall_score)

        explanation = await self._gemini_service.generate_explanation(
            recommended_crop=request.crop,
            estimated_profit=profit_result["estimated_profit"],
            disease=pest_result["disease"],
            pest_score=scores["pest_score"],
            weather_score=scores["weather_score"],
            market_score=scores["market_score"],
            overall_score=overall_score,
            recommendation=recommendation,
            warnings=rule_result["warnings"],
        )

        response = DecisionResponse(
            recommended_crop=request.crop,
            estimated_profit=profit_result["estimated_profit"],
            disease=pest_result["disease"],
            pest_score=scores["pest_score"],
            weather_score=scores["weather_score"],
            market_score=scores["market_score"],
            overall_score=overall_score,
            confidence=overall_confidence,
            recommendation=recommendation,
            warnings=rule_result["warnings"],
            explanation=explanation,
        )

        logger.info("Decision engine completed: recommendation=%s", recommendation)
        return response