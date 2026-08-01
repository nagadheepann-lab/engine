from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self) -> None:
        self._api_key: str = os.environ.get("OPENWEATHER_API_KEY", "")
        self._base_url: str = "https://api.openweathermap.org/data/2.5/weather"
        self._use_mock: bool = os.environ.get("USE_MOCK_WEATHER", "true").lower() == "true"

    async def get_weather(self, state: str, district: str) -> dict[str, Any]:
        if self._use_mock or not self._api_key:
            return self._get_mock_weather(state, district)
        return await self._fetch_from_api(state, district)

    async def _fetch_from_api(self, state: str, district: str) -> dict[str, Any]:
        import httpx

        params = {
            "q": f"{district},{state},IN",
            "appid": self._api_key,
            "units": "metric",
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(self._base_url, params=params)
                response.raise_for_status()
                data = response.json()
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            rainfall = data.get("rain", {}).get("1h", 0)
            weather_score = self._compute_weather_score(temperature, humidity, rainfall)
            logger.info(
                "Weather fetched: temp=%.1f, humidity=%.1f, rainfall=%.1f",
                temperature,
                humidity,
                rainfall,
            )
            return {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "rainfall": round(rainfall, 1),
                "weather_score": weather_score,
            }
        except Exception as exc:
            logger.error("Weather API failed: %s", exc)
            return self._get_mock_weather(state, district)

    def _get_mock_weather(self, state: str, district: str) -> dict[str, Any]:
        logger.info("Using mock weather data for %s, %s", district, state)
        return {
            "temperature": 31,
            "humidity": 84,
            "rainfall": 620,
            "weather_score": 86,
        }

    def _compute_weather_score(
        self, temperature: float, humidity: float, rainfall: float
    ) -> float:
        score = 100.0
        if temperature < 10 or temperature > 40:
            score -= 30
        elif temperature < 15 or temperature > 35:
            score -= 15
        if humidity < 30 or humidity > 90:
            score -= 20
        elif humidity < 40 or humidity > 80:
            score -= 10
        if rainfall < 100:
            score -= 25
        elif rainfall < 300:
            score -= 10
        return max(0, min(100, round(score, 1)))