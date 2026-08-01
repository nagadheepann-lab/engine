from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models" / "pest"


class PestService:
    def __init__(self) -> None:
        self._model: Any | None = None
        self._class_names: list[str] = []
        self._preprocessing: dict[str, Any] = {}
        self._loaded: bool = False

    def load(self) -> None:
        if self._loaded:
            return

        try:
            import tensorflow as tf
        except ImportError as exc:
            logger.error("TensorFlow is required for PestService: %s", exc)
            raise

        model_path = MODELS_DIR / "pest_classifier.keras"
        if not model_path.exists():
            raise FileNotFoundError(f"Pest model not found at {model_path}")

        self._model = tf.keras.models.load_model(str(model_path))
        logger.info("Pest classifier model loaded from %s", model_path)

        class_names_path = MODELS_DIR / "class_names.json"
        if class_names_path.exists():
            with open(class_names_path, "r", encoding="utf-8") as f:
                self._class_names = json.load(f)
        else:
            logger.warning("class_names.json not found at %s", class_names_path)
            self._class_names = []

        preprocessing_path = MODELS_DIR / "preprocessing.json"
        if preprocessing_path.exists():
            with open(preprocessing_path, "r", encoding="utf-8") as f:
                self._preprocessing = json.load(f)
        else:
            logger.warning("preprocessing.json not found at %s", preprocessing_path)
            self._preprocessing = {"target_size": [224, 224]}

        self._loaded = True
        logger.info("PestService initialized successfully")

    def predict(self, image_path: str) -> dict[str, Any]:
        if not self._loaded:
            self.load()

        if self._model is None:
            raise RuntimeError("Pest model is not loaded")

        try:
            img = Image.open(image_path).convert("RGB")
        except Exception as exc:
            logger.error("Failed to open image %s: %s", image_path, exc)
            return {"disease": "Unknown", "confidence": 0.0}

        target_size = tuple(self._preprocessing.get("target_size", [224, 224]))
        img = img.resize(target_size)

        img_array = np.array(img, dtype=np.float32)
        img_array = img_array / 255.0

        if img_array.ndim == 3:
            img_array = np.expand_dims(img_array, axis=0)

        try:
            predictions = self._model.predict(img_array, verbose=0)
            predicted_index = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][predicted_index])
            disease = (
                self._class_names[predicted_index]
                if predicted_index < len(self._class_names)
                else "Unknown"
            )
        except Exception as exc:
            logger.error("Prediction failed: %s", exc)
            return {"disease": "Unknown", "confidence": 0.0}

        logger.info(
            "Pest prediction: disease=%s, confidence=%.4f", disease, confidence
        )
        return {"disease": disease, "confidence": confidence}