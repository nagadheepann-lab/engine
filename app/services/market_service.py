from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class MarketService:
    def __init__(self) -> None:
        self._use_mock: bool = os.environ.get("USE_MOCK_MARKET", "true").lower() == "true"

    async def get_market_data(self, crop: str) -> dict[str, Any]:
        if self._use_mock:
            return self._get_mock_market_data(crop)
        return await self._fetch_from_api(crop)

    async def _fetch_from_api(self, crop: str) -> dict[str, Any]:
        import httpx

        api_url = os.environ.get("AGMARKNET_API_URL", "")
        if not api_url:
            logger.warning("AGMARKNET_API_URL not set, falling back to mock data")
            return self._get_mock_market_data(crop)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(api_url, params={"commodity": crop})
                response.raise_for_status()
                data = response.json()
            price = data.get("price", 0)
            trend = data.get("trend", "Stable")
            market_score = self._compute_market_score(trend)
            logger.info(
                "Market data fetched: crop=%s, price=%s, trend=%s",
                crop,
                price,
                trend,
            )
            return {"price": price, "trend": trend, "market_score": market_score}
        except Exception as exc:
            logger.error("Market API failed: %s", exc)
            return self._get_mock_market_data(crop)

    def _get_mock_market_data(self, crop: str) -> dict[str, Any]:
        logger.info("Using mock market data for crop: %s", crop)
        return {"price": 6400, "trend": "Rising", "market_score": 78}

    def _compute_market_score(self, trend: str) -> float:
        trend_scores = {
            "Rising": 90,
            "Stable": 70,
            "Falling": 30,
        }
        return float(trend_scores.get(trend, 70))