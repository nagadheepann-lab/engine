from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models" / "profit"


class ProfitService:
    def __init__(self) -> None:
        self._model: Any | None = None
        self._scaler: Any | None = None
        self._loaded: bool = False

    def load(self) -> None:
        if self._loaded:
            return

        try:
            import joblib
        except ImportError as exc:
            logger.error("joblib is required for ProfitService: %s", exc)
            raise

        model_path = MODELS_DIR / "profit_model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Profit model not found at {model_path}")

        self._model = joblib.load(str(model_path))
        logger.info("Profit model loaded from %s", model_path)

        scaler_path = MODELS_DIR / "scaler.pkl"
        if scaler_path.exists():
            self._scaler = joblib.load(str(scaler_path))
            logger.info("Scaler loaded from %s", scaler_path)

        self._loaded = True
        logger.info("ProfitService initialized successfully")

    def predict(
        self,
        temperature: float,
        humidity: float,
        rainfall: float,
        budget: float,
        land_area: float,
        expected_selling_price: float,
    ) -> dict[str, Any]:
        if not self._loaded:
            self.load()

        if self._model is None:
            raise RuntimeError("Profit model is not loaded")

        features = np.array([
            [temperature, humidity, rainfall, budget, land_area, expected_selling_price],
        ], dtype=np.float64)

        if self._scaler is not None:
            features = self._scaler.transform(features)

        try:
            estimated_profit = float(self._model.predict(features)[0])
        except Exception as exc:
            logger.error("Profit prediction failed: %s", exc)
            estimated_profit = 0.0

        confidence = self._compute_confidence(estimated_profit)

        logger.info(
            "Profit prediction: estimated_profit=%.2f, confidence=%.4f",
            estimated_profit,
            confidence,
        )
        return {"estimated_profit": round(estimated_profit, 2), "confidence": confidence}

    def _compute_confidence(self, estimated_profit: float) -> float:
        if estimated_profit <= 0:
            return 0.1
        if estimated_profit < 10000:
            return 0.5
        if estimated_profit < 50000:
            return 0.7
        if estimated_profit < 100000:
            return 0.85
        return 0.95