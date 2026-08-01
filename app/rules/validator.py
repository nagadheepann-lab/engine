from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RuleEngine:
    def __init__(self) -> None:
        self._min_budget_map: dict[str, float] = {
            "Groundnut": 25000,
            "Soybean": 20000,
            "Mustard": 15000,
            "Sunflower": 18000,
            "Sesame": 12000,
        }
        self._water_intensive_crops: list[str] = [
            "Rice",
            "Sugarcane",
            "Banana",
            "Paddy",
        ]
        self._crop_temp_tolerance: dict[str, dict[str, float]] = {
            "Groundnut": {"min": 20, "max": 40},
            "Soybean": {"min": 15, "max": 38},
            "Mustard": {"min": 5, "max": 30},
            "Sunflower": {"min": 10, "max": 40},
            "Sesame": {"min": 15, "max": 38},
        }

    def validate(
        self,
        crop: str,
        budget: float,
        water_availability: str,
        temperature: float,
        land_area: float,
    ) -> dict[str, Any]:
        warnings: list[str] = []
        passed: bool = True

        passed = self._check_budget(crop, budget, warnings) and passed
        passed = self._check_water(crop, water_availability, warnings) and passed
        passed = self._check_temperature(crop, temperature, warnings) and passed
        passed = self._check_land_area(land_area, warnings) and passed

        result = {"passed": passed, "warnings": warnings}
        logger.info("Rule engine result: passed=%s, warnings=%s", passed, warnings)
        return result

    def _check_budget(self, crop: str, budget: float, warnings: list[str]) -> bool:
        min_budget = self._min_budget_map.get(crop, 15000)
        if budget < min_budget:
            warnings.append(
                f"Budget Rs {budget} is below minimum cultivation cost Rs {min_budget} for {crop}"
            )
            return False
        return True

    def _check_water(
        self, crop: str, water_availability: str, warnings: list[str]
    ) -> bool:
        low_water = water_availability.lower() in ("low", "very low", "scarce")
        if low_water and crop in self._water_intensive_crops:
            warnings.append(
                f"Water availability is low; {crop} is water-intensive and not recommended"
            )
            return False
        return True

    def _check_temperature(
        self, crop: str, temperature: float, warnings: list[str]
    ) -> bool:
        tolerance = self._crop_temp_tolerance.get(crop)
        if tolerance is None:
            return True
        if temperature < tolerance["min"] or temperature > tolerance["max"]:
            warnings.append(
                f"Temperature {temperature}C is outside {crop} tolerance range "
                f"({tolerance['min']}-{tolerance['max']}C)"
            )
            return False
        return True

    def _check_land_area(self, land_area: float, warnings: list[str]) -> bool:
        if land_area < 0.5:
            warnings.append(
                f"Land area {land_area} acres is very small for commercial cultivation"
            )
            return False
        return True